import datetime
import json
import os
import statistics

import filetype
from PIL import Image as PilImage
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from loguru import logger
from rest_framework import serializers

from scoring.decorators import count_calls
from scoring.excel import create_xlsx
from scoring.helper import get_project_evaluation_dir, save_check_dir, get_path_backup, dlog, \
    set_logging_file, INFO_FILE_NAME, is_image, elog, get_rel_path, get_path_projects, ilog, calculate_md5_hash
from server.settings import BASE_DIR

KEY_LEN = 32


class TimestampField(serializers.Field):
    def to_representation(self, value):
        # Convert the datetime value to a timestamp
        if value is None:
            return None
        return int(value.timestamp() * 1000)

    def to_internal_value(self, data):
        # Convert the timestamp to a datetime value
        try:
            dt = datetime.datetime.fromtimestamp(int(data))
            return dt
        except (ValueError, TypeError):
            raise serializers.ValidationError("Invalid timestamp")


class Project(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)
    icon = models.CharField(max_length=5, null=True, default="", blank=True)

    image_dir = models.CharField(max_length=500,
                                 validators=[RegexValidator('^(?!setup$|backup$|evaluations$).*$')],
                                 null=True, blank=True)
    users = models.ManyToManyField(User)

    wanted_scores_per_user = models.IntegerField(default=100, null=True, blank=True)
    wanted_scores_per_image = models.IntegerField(default=2, null=True, blank=True)

    def evaluate_data(self, data):
        _path = get_project_evaluation_dir(str(self.pk))

        _file_template = datetime.datetime.now().strftime("%Y-%m-%d_-_%H%M%S")
        _filename = os.path.join(_path, f"{_file_template}.json")
        with open(_filename, "w") as _file:
            json.dump(data, _file, ensure_ascii=True, indent=4)

        with open(_filename, "r") as _file:
            data = json.load(_file)
            dlog("evaluate_data", data.get("imagefiles"))

    def get_scoring_users(self, _exclude=None):
        req = self.users.exclude(username=_exclude) if _exclude else self.users.all()
        return req.filter(scores__project__pk=self.pk, scores__is_completed=True).distinct().order_by("pk")

    def get_max_score(self):
        score = 0
        features = self.features.all()
        for ft in features:
            score += ft.option_count
        return score, len(features)

    def get_features_flat(self):
        return self.features.all().values_list("name", flat=True)

    def get_data(self, user):
        data = {"imagesTotal": self.get_all_files_save().count()}
        return data | self.get_scores(user)

    def get_scores(self, user):
        scores = self.get_all_scores_save()
        data = {
            "scoresCount": scores.count(),
            "scoresOwn": scores.filter(user=user).count(),
            "uselessCount": self.files.filter(useless=True, hidden=False).count()
        }
        return data

    def get_all_scores_save(self):
        return self.scores.exclude(file__useless=True).filter(user__in=self.users.all(), is_completed=True)

    def get_score_count(self):
        return self.get_all_scores_save().count()

    def get_all_files_save(self):
        return self.files.exclude(useless=True)

    def get_all_useless_files(self):
        return self.files.filter(useless=True)

    def get_files_count(self):
        return self.get_all_files_save().count()

    def is_finished(self):
        return self.get_score_count() >= self.get_files_count() * self.wanted_scores_per_image

    def calc_fleiss_kappa(self):
        from statsmodels.stats.inter_rater import fleiss_kappa

        scoring_fields = self.get_features_flat()
        summed = {}
        result = {}

        for _file in self.get_all_files_save():
            scores = _file.get_scores_save(self)
            #sums = np.zeros(len(scoring_fields) + 1)
            matrix = []
            counts = [{"0": 0, "1": 0, "2": 0, "X": 0} for _ in range(len(scores))]

            for score in scores:
                row = score.as_row(scoring_fields)
                matrix.append(row)

                for idx, value in enumerate(row):
                    if value == 0:
                        counts[idx]["0"] += 1
                    elif value == 1:
                        counts[idx]["1"] += 1
                    elif value == 2:
                        counts[idx]["2"] += 1
                    else:
                        counts[idx]["X"] += 1

            print(f"{_file.filename} => {matrix}")

            for idx, feature in enumerate(scoring_fields):
                elements = summed.get(feature, [])
                elements.append(list(counts[idx].values()))
                summed.update({feature: elements})
        print("SUMMED", summed)

        for idx, feature in enumerate(scoring_fields):
            data = summed.get(feature)
            kappa = fleiss_kappa(data)
            result.update({feature: f"{kappa:.4f}"})

        return result

    def evaluate_data_as_xlsx(self, data):
        _image_files = self.get_all_files_save()
        dlog(f"Recalculate Std-Deviation for {len(_image_files)} ImageFiles...")
        for _file in _image_files:
            _file.calc_std_dev()

        return create_xlsx(self, data, _image_files)

    def get_existing_evaluations(self) -> dict:
        files = os.listdir(get_project_evaluation_dir(str(self.pk)))
        return {"files": files}

    def get_images_dir(self):
        return get_path_projects(str(self.image_dir))

    def check_create_infofiles(self):
        _path = self.get_images_dir()
        for root, _, files in os.walk(_path):
            if len(files):
                if INFO_FILE_NAME not in files:
                    self.create_infofile(root, files)

    @staticmethod
    def create_infofile(_path, _files):
        if len(_files) == 0:
            return False

        with open(os.path.join(_path, INFO_FILE_NAME), "w") as _file:
            _file.write(
                "This is a helper-file which lists all the available images. Two were picked. If one of these is marked 'useless' the next will be chosen!\n")
            _file.write("Starting below ###...\n")
            _file.write("####################\n")
            for image in _files:
                if image == INFO_FILE_NAME:
                    continue
                _file.write(f"{image}\n")

        return True

    def create_script(self):
        set_logging_file()
        _path = self.get_images_dir()
        for root, _, files in os.walk(_path):
            group_trigger = False
            dir_count = 0
            logger.info(f"Create Script for {root} => {files}")

            for _file in files:
                group_trigger = not group_trigger
                if group_trigger:
                    dir_count += 1
                    save_check_dir(os.path.join(root, str(dir_count)))

                os.rename(os.path.join(root, _file),
                          os.path.join(root, str(dir_count), _file))

    def read_images(self, enabled_log=True):
        set_logging_file()
        files, folders = 0, 0
        _path = self.get_images_dir()

        for _, dirs, filenames in os.walk(_path):
            files += len(filenames)
            folders += len(dirs)
        dlog(f"Project has: {files} Files in {folders} Folders, {_path=}")

        if folders <= 1:
            self.create_script()
            self.check_create_infofiles()

        info_files = []
        for root, _, files in os.walk(_path):
            if len(files):
                if enabled_log:
                    logger.info(f"Read Images for '{root}' => {files}")
                for _file in files:
                    if _file.endswith(".txt"):
                        info_files.append(os.path.join(BASE_DIR, root))

        for info_file in info_files:
            self.parse_info_file(info_file, enabled_log)

        return True

    def parse_info_file(self, _path, enabled_log=True, get_or_create_amount=2):
        set_logging_file()
        _path_infofile = os.path.join(_path, INFO_FILE_NAME)
        files = []
        dlog(f"\nParse Infofile! {_path=}, {get_or_create_amount=}")

        if not os.path.exists(_path_infofile):
            return None, files

        with open(_path_infofile, "r") as f:
            lines = f.readlines()
            images = lines[3:]

        for img in images:
            _file = img.rstrip("\n")
            if len(_file) == 0:
                break

            full_path = os.path.join(_path, _file)

            if not os.path.exists(full_path):
                elog(full_path, tag="[MISSING]")
                continue

            if not filetype.is_image(full_path):
                continue

            if get_or_create_amount == 0:
                return True, files

            image_file, created = ImageFile.objects.get_or_create(project=self, filename=_file,
                                                                  path=get_rel_path(_path))
            files.append(image_file)

            dlog(f"=> {_file=}, {full_path}, {created=}, Useless={image_file.useless}")
            if created:
                if enabled_log:
                    logger.info(f"Created ImageFile for {full_path} #{get_or_create_amount}")

                if is_image(full_path):
                    with PilImage.open(full_path) as im:
                        w, h = im.size
                        image_file.width = w
                        image_file.height = h
                image_file.calc_hash()
                image_file.date = timezone.now()
                image_file.save()
                get_or_create_amount -= 1

            else:
                if not image_file.useless:
                    if enabled_log:
                        logger.info(f"Existing ImageFile for {full_path} #{get_or_create_amount}")
                    get_or_create_amount -= 1

        if get_or_create_amount == 0:
            return True, files

        elog(f"Should never be reached... | {get_or_create_amount=}")
        return False, files


    def __str__(self):
        _id = ""
        if os.getenv("DEBUG"):
            _id = f"[{self.pk}] "
        return f"{_id} Project: {self.name}"


class ScoreFeature(models.Model):
    project = models.ForeignKey(Project, related_name="features", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False)
    bit = models.IntegerField(default=0, null=False, blank=True)
    option_count = models.IntegerField(default=3, null=False, blank=True)

    def __str__(self):
        _id = ""
        if os.getenv("DEBUG"):
            _id = f"[{self.pk}] "
        return f"{_id} Project: {self.project} > {self.name}, bit={self.bit}"


class ImageFile(models.Model):
    project = models.ForeignKey(Project, related_name="files", on_delete=models.CASCADE)
    filename = models.CharField(max_length=50, null=False)
    path = models.CharField(max_length=500, null=False)
    useless = models.BooleanField(default=False)
    raw_hash = models.CharField(max_length=KEY_LEN, null=True, blank=True)
    hidden = models.BooleanField(default=False)
    stddev = models.FloatField(default=0, null=True, blank=True)

    data = models.JSONField(blank=True, default=dict)

    width = models.IntegerField(default=0, null=False, blank=True)
    height = models.IntegerField(default=0, null=False, blank=True)

    frame_x = models.IntegerField(default=0, null=False, blank=True)
    frame_y = models.IntegerField(default=0, null=False, blank=True)
    frame_w = models.IntegerField(default=0, null=False, blank=True)
    frame_h = models.IntegerField(default=0, null=False, blank=True)

    date = models.DateTimeField(blank=True, null=True)

    def get_scores_save(self, project: Project):
        return self.scores.exclude(file__useless=True).filter(user__in=project.users.all())

    def calc_hash(self):
        self.raw_hash = calculate_md5_hash(self.get_path())

    @count_calls
    def calc_std_dev(self, save=True, users=None):
        scores = self.get_scores_save(self.project)
        scoring_fields = self.project.get_features_flat()
        if len(scoring_fields) == 0:
            elog("No ScoreFeatures found!")
            return

        if users:
            scores = scores.filter(user__in=users)

        n = scores.distinct("user").count()
        if n >= 2:

            stddev = 0
            stddev_list = {key: [] for key in scoring_fields}

            for score in scores:
                _data = score.data
                for val in scoring_fields:
                    score_value = _data.get(val)
                    if score_value is not None and score_value != 'X':
                        feature = stddev_list.get(val)
                        feature.append(score_value)
                        stddev_list.update({val: feature})

            for key, _list in stddev_list.items():
                dlog(key, "=>", _list)
                if len(_list) < 2:
                    continue
                _stddev = round(statistics.pstdev(_list), 2)
                stddev += _stddev
                self.data.update({f"stddev_{key}": _stddev})
            self.stddev = round(stddev, 2)
            dlog("V=", self.stddev, "\n")
            if save:
                self.save()
            return self.stddev
        return 0

    def get_path(self):
        _abs_path = os.path.abspath(BASE_DIR)
        return os.path.join(_abs_path, *[self.path, self.filename])

    def get_rel_path(self):
        return get_rel_path(self.path)

    def get_video_source(self):
        _path_infofile = os.path.join(self.path, INFO_FILE_NAME)
        if os.path.exists(_path_infofile):
            with open(_path_infofile, "r") as f:
                for line in f.readlines():
                    if line.startswith("video:"):
                        return line[7:].rstrip()

    def get_scored_users(self):
        return list(self.scores.order_by("user__username").values_list("user__username", flat=True))

    def fix_path(self):
        if '\\' in self.path:
            self.path = self.path.replace('\\', '/')
            self.save()
            ilog("Fixxed", self, tag="[DONE]")

    def __str__(self):
        _id = ""
        if os.getenv("DEBUG"):
            _id = f"[{self.pk}] "
        add_0 = "🗑 " if self.useless else ""
        return f"{add_0}{_id} File: {self.filename} for '{self.project.name}'"


class ImageScore(models.Model):
    user = models.ForeignKey(User, related_name="scores", on_delete=models.CASCADE)
    file = models.ForeignKey(ImageFile, related_name="scores", on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name="scores", on_delete=models.CASCADE)
    comment = models.CharField(max_length=255, null=True, default="", blank=True)

    data = models.JSONField(blank=True, default=dict)
    date = models.DateTimeField(auto_created=True, null=True, blank=True)

    is_completed = models.BooleanField(default=False)

    def check_completed(self):
        scoring_fields = self.project.get_features_flat()
        for _field in scoring_fields:
            if self.data.get(_field) is None:
                return False
        self.is_completed = True
        self.save()
        return True

    def as_row(self, _fields):
        row = []
        for _field in _fields:
            row.append(self.data.get(_field))
        return row

    def __str__(self):
        def readable(_field):
            return str(_field) if _field is not None else "?"

        _id = ""
        if os.getenv("DEBUG"):
            _id = f"[{self.pk}] "

        scores = ""
        scoring_fields = self.project.get_features_flat()
        for _field in scoring_fields:
            _data = self.data.get(_field)
            scores += readable(_data)

        add_0 = f" Comment: {self.comment}" if self.comment else ""

        return f"{_id} Score: {scores} for '{self.file.filename}' by {self.user.username}{add_0}"


class Backup(models.Model):
    name = models.CharField(max_length=100, null=False)
    date = models.DateTimeField(null=True, blank=True)

    def get_file(self):
        return get_path_backup(self.name)

    def __str__(self):
        _id = ""
        if os.getenv("DEBUG"):
            _id = f"[{self.pk}] "
        return f"{_id} {self.name}"
