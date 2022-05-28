import datetime
import json
import os
import re
import pandas as pd
import statistics

from django.core.validators import RegexValidator

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from scoring.helper import get_project_evaluation_dir, get_media_path, save_check_dir, get_path_backup

from server.settings import BASE_DIR



class Project(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)
    image_dir = models.CharField(max_length=500,
                                 validators=[RegexValidator('^(?!setup$|backup$|evaluations$).*$')],
                                 null=True,
                                 blank=True)
    users = models.ManyToManyField(User)

    wanted_scores_per_user = models.IntegerField(default=100, null=True, blank=True)
    wanted_scores_per_image = models.IntegerField(default=2, null=True, blank=True)

    def evaluate_data(self, data):
        _path = get_project_evaluation_dir(str(self.pk))

        _file_template = datetime.datetime.now().strftime("%Y-%m-%d_-_%H%M%S")
        with open(os.path.join(_path, f"{_file_template}.json"), "w") as _file:
            json.dump(data, _file, ensure_ascii=True, indent=4)

        with open(os.path.join(_path, f"{_file_template}.json"), "r") as _file:
            data = json.load(_file)
            print("DATA", data.get("imagefiles"))


    def get_all_scores_save(self):
        return self.scores.exclude(file__useless=True) \
                          .filter(user__in=self.users.all())

    def get_score_count(self):
        return self.get_all_scores_save().count()

    def get_all_files_save(self):
        return self.files.exclude(useless=True)

    def get_files_count(self):
        return self.get_all_files_save().count()

    def is_finished(self):
        return self.get_score_count() >= self.get_files_count() * self.wanted_scores_per_image

    def evaluate_data_as_xlsx(self, data):

        def get_cell(value) -> str:

            if value < 65:
                raise Exception("Unexpected value", value)
            if value <= 90:
                return chr(value)

            init = 64  # pre char 'A'

            while value > 90:
                value -= 26
                init += 1

            if init == 64:
                return chr(value)
            else:
                return f"{chr(init)}{chr(value)}"

        _path = get_project_evaluation_dir(str(self.pk))
        project = Project.objects.get(name=data.get("project").get("name"))
        user_ids = project.get_all_scores_save().distinct("user").values_list("user__id", flat=True)
        user_id_dict = {}

        _file_template = datetime.datetime.now().strftime("%Y-%m-%d_-_%H%M%S")

        df = pd.DataFrame()

        project_name = project.name
        target = os.path.join(_path, f"{_file_template}.xlsx")
        writer = pd.ExcelWriter(target, engine='xlsxwriter')
        df.to_excel(writer, sheet_name=project_name)

        ws = writer.sheets[project_name]
        # workbook = writer.book
        # format_OK = workbook.add_format({'bg_color': '#00a077'})

        header = ["ID", "Path", "Filename", "Useless"]
        i = 0
        for u_id in user_ids:
            user_id_dict.update({u_id: i})
            header.extend([f"Eyes_Scorer{u_id}",
                           f"Nose_Scorer{u_id}",
                           f"Cheeks_Scorer{u_id}",
                           f"Ears_Scorer{u_id}",
                           f"Whiskers_Scorer{u_id}",
                           f"Sum_Scorer{u_id}",
                           f"Mean_Scorer{u_id}"])
            i += 1

        for u_id in user_ids:
            header.append(f"Comment_Scorer{u_id}")
        header.extend([f"Varianz-Eyes",
                       f"Varianz-Nose",
                       f"Varianz-Cheeks",
                       f"Varianz-Ears",
                       f"Varianz-Whiskers",
                       f"Varianz (SUM)"])

        for i, name in enumerate(header, start=0):
            ws.write(0, i, name)

        line = 1

        for image_file in project.files.filter(scores__gt=0):
            queryset = image_file.get_all_scores_save(self).order_by("user__pk")

            ws.write(line, 0, line)
            ws.write(line, 1, image_file.path)
            ws.write(line, 2, image_file.filename)
            ws.write(line, 3, image_file.useless)

            # Write user-comments
            pos = user_id_dict.get(max(user_id_dict, key=user_id_dict.get))
            last_pos = 10 + (pos * 7)
            i = last_pos + 1
            for score in queryset:
                ws.write(line, i, score.comment)
                i += 1

            # Write varianz
            ws.write(line, i, image_file.varianz_eye)
            ws.write(line, i + 1, image_file.varianz_nose)
            ws.write(line, i + 2, image_file.varianz_cheek)
            ws.write(line, i + 3, image_file.varianz_ear)
            ws.write(line, i + 4, image_file.varianz_whiskers)
            ws.write(line, i + 5, image_file.varianz)

            # TODO format later
            #
            # _list = [image_file.varianz_eye,
            #          image_file.varianz_nose,
            #          image_file.varianz_cheek,
            #          image_file.varianz_ear,
            #          image_file.varianz_whiskers]
            # j = 0
            # for val in _list:
            #     j += 1
            #     if val == 0:
            #         print("OKAY", i, j)
            #         ws.set_column(i + j, i + j, cell_format=format_OK)

            # Write Data
            for score in queryset:
                pos = user_id_dict.get(score.user_id)

                start_col = get_cell(65 + 4 + (pos * 7))
                ws.write(line, 4 + (pos * 7), score.s_eye)
                ws.write(line, 5 + (pos * 7), score.s_nose)
                ws.write(line, 6 + (pos * 7), score.s_cheek)
                ws.write(line, 7 + (pos * 7), score.s_ear)
                ws.write(line, 8 + (pos * 7), score.s_whiskers)
                end_col = get_cell(65 + 8 + (pos * 7))

                if score.s_eye is not None or \
                   score.s_nose is not None or \
                   score.s_cheek is not None or \
                   score.s_ear is not None or \
                   score.s_whiskers is not None:
                    ws.write_formula(line,  9 + (pos * 7), f"=SUM({start_col}{line + 1}:{end_col}{line + 1})")
                    ws.write_formula(line, 10 + (pos * 7), f"=AVERAGE({start_col}{line + 1}:{end_col}{line + 1})")

            line += 1

        writer.save()

        return target

    def get_existing_evaluations(self) -> dict:
        files = os.listdir(get_project_evaluation_dir(str(self.pk)))
        return {"files": files}

    def get_images_dir(self):
        return os.path.join(get_media_path(), self.image_dir)

    def check_create_infofiles(self):
        _path = self.get_images_dir()
        for root, _, files in os.walk(_path):
            if len(files):
                if not ("infofile.txt" in files):
                    self.create_infofile(root, files)

    @staticmethod
    def create_infofile(_path, _files):
        if len(_files) == 0:
            return False

        with open(os.path.join(_path, "infofile.txt"), "w") as _file:
            _file.write("\n")
            _file.write("\n")
            _file.write("\n")
            for image in _files:
                if image == "infofile.txt":
                    continue
                _file.write(f"{image}\n")

        return True

    def create_script(self):
        _path = self.get_images_dir()
        for root, _, files in os.walk(_path):
            if len(files):
                print("CREATE SCRIPT", root, files)
                group_trigger = False
                dir_count = 0
                for _file in files:
                    group_trigger = not group_trigger
                    if group_trigger:
                        dir_count += 1
                        save_check_dir(os.path.join(root, str(dir_count)))

                    os.rename(os.path.join(root, _file),
                              os.path.join(root, str(dir_count), _file))

    def read_images(self):
        _path = self.get_images_dir()
        for root, _, files in os.walk(_path):
            if len(files):
                # print("READ IMAGES", root, files)
                for _file in files:
                    if _file[-4:] == ".txt":  # TODO check file-type
                        self.parse_info_file(os.path.join(BASE_DIR, root))

        return True

    def parse_info_file(self, _path, get_or_create_amount=2):

        regex = re.compile("^\d{5}\.png")
        _path_infofile = os.path.join(_path, "infofile.txt")
        if os.path.exists(_path_infofile):
            with open(_path_infofile, 'r') as f:
                lines = f.readlines()
                images = lines[3:]

                for img in images:

                    if not regex.match(img):
                        break

                    if get_or_create_amount == 0:
                        return True

                    _file = img.rstrip("\n")

                    image_file, created = ImageFile.objects.get_or_create(project=self,
                                                                          filename=_file,
                                                                          path=_path)

                    if created:
                        print("Created IMAGEFILE", _file, get_or_create_amount, _path)
                        image_file.date = timezone.now()
                        image_file.save()
                        get_or_create_amount -= 1

                    else:
                        if not image_file.useless and not image_file.hidden:
                            print("Existing IMAGEFILE", _file, get_or_create_amount, _path)
                            get_or_create_amount -= 1
        return False

    def __str__(self):
        _id = ""
        if os.getenv("DEBUG"):
            _id = f"[{self.pk}] "
        return f"{_id} Project: {self.name}"


class ImageFile(models.Model):
    project = models.ForeignKey(Project, related_name='files', on_delete=models.CASCADE)
    filename = models.CharField(max_length=50, null=False)
    path = models.CharField(max_length=500, null=False)
    useless = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    varianz = models.FloatField(default=0, null=True, blank=True)

    varianz_eye = models.FloatField(default=None, null=True, blank=True)
    varianz_nose = models.FloatField(default=None, null=True, blank=True)
    varianz_cheek = models.FloatField(default=None, null=True, blank=True)
    varianz_ear = models.FloatField(default=None, null=True, blank=True)
    varianz_whiskers = models.FloatField(default=None, null=True, blank=True)

    date = models.DateTimeField(blank=True, null=True)

    def get_scores_save(self, project: Project):
        return self.scores.exclude(file__useless=True) \
                   .filter(user__in=project.users.all())

    def calc_varianz(self):
        _params = ["s_eye", "s_nose", "s_cheek", "s_ear", "s_whiskers"]

        scores = self.get_scores_save(self.project)

        n = scores.distinct("user").count()
        if n >= 2:

            varianz = 0
            varianz_list = {
                "s_eye": [],
                "s_nose": [],
                "s_cheek": [],
                "s_ear": [],
                "s_whiskers": []
            }

            for score in scores:
                for val in _params:
                    score_value = getattr(score, val)
                    if score_value is not None:
                        feature = varianz_list.get(val)
                        feature.append(score_value)
                        varianz_list.update({val: feature})

            for key, _list in varianz_list.items():
                # print(key, "=>", _list)
                if len(_list) < 2:
                    continue
                _varianz = round(statistics.pstdev(_list), 2)
                varianz += _varianz
                setattr(self, f"varianz_{key[2:]}", _varianz)
            self.varianz = round(varianz, 2)
            self.save()
            # print("V=", self.varianz, "\n")
            return self.varianz
        return 0

    def __str__(self):
        _id = ""
        if os.getenv("DEBUG"):
            _id = f"[{self.pk}] "
        return f"{_id} File: {self.filename} for project {self.project.name}"

    def get_rel_path(self):
        index = self.path.find("media")
        return self.path[index+6:]


class ImageScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(ImageFile, related_name='scores', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='scores', on_delete=models.CASCADE)
    comment = models.CharField(max_length=255, null=True, default="", blank=True)

    s_eye = models.IntegerField(default=None, null=True, blank=True)
    s_nose = models.IntegerField(default=None, null=True, blank=True)
    s_cheek = models.IntegerField(default=None, null=True, blank=True)
    s_ear = models.IntegerField(default=None, null=True, blank=True)
    s_whiskers = models.IntegerField(default=None, null=True, blank=True)
    
    date = models.DateTimeField(auto_created=True, null=True, blank=True)

    def __str__(self):
        _id = ""
        if os.getenv("DEBUG"):
            _id = f"[{self.pk}] "
        return f"{_id} Score: {self.s_eye}{self.s_nose}{self.s_cheek}{self.s_ear}{self.s_whiskers} for '{self.file.filename}' by {self.user.username}"


class Backup(models.Model):
    name = models.CharField(max_length=100, null=False)

    def get_file(self):
        return get_path_backup(self.name)

    def __str__(self):
        _id = ""
        if os.getenv("DEBUG"):
            _id = f"[{self.pk}] "
        return f"{_id} {self.name}"
