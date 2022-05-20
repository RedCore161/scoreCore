import datetime
import json
import math
import os
import random
import re
import pandas as pd

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.utils import timezone

from scoring.helper import get_project_evaluation_dir, get_media_path, save_check_dir


from server.settings import BASE_DIR


class Project(models.Model):
    name = models.CharField(max_length=100, null=False)
    image_dir = models.CharField(max_length=500, null=True, blank=True)
    users = models.ManyToManyField(User)

    def evaluate_data(self, data):
        _path = get_project_evaluation_dir(str(self.pk))

        _file_template = datetime.datetime.now().strftime("%Y-%m-%d_-_%H%M%S")
        with open(os.path.join(_path, f"{_file_template}.json"), "w") as _file:
            json.dump(data, _file, ensure_ascii=True, indent=4)

        with open(os.path.join(_path, f"{_file_template}.json"), "r") as _file:
            data = json.load(_file)
            print("DATA", data.get("imagefiles"))

    def evaluate_data_as_xlsx(self, data):
        _path = get_project_evaluation_dir(str(self.pk))
        project = Project.objects.get(name=data.get("project").get("name"))
        user_ids = project.scores.all().distinct("user").values_list("user__id", flat=True)
        user_id_dict = {}

        _file_template = datetime.datetime.now().strftime("%Y-%m-%d_-_%H%M%S")

        df = pd.DataFrame()

        project_name = project.name
        target = os.path.join(_path, f"{_file_template}.xlsx")
        writer = pd.ExcelWriter(target, engine='xlsxwriter')
        df.to_excel(writer, sheet_name=project_name)

        ws = writer.sheets[project_name]

        header = ["ID", "Path", "Filename"]
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

        for i, name in enumerate(header, start=0):
            ws.write(0, i, name)

        line = 1

        for image_file in project.files.filter(scores__gt=0):
            ws.write(line, 0, line)
            ws.write(line, 1, image_file.path)
            ws.write(line, 2, image_file.filename)

            for score in image_file.scores.all().order_by("user__pk"):
                pos = user_id_dict.get(score.user_id)

                start_col = chr(68 + (pos * 7))
                end_col = chr(72 + (pos * 7))
                ws.write(line, 3 + (pos * 7), score.s_eye)
                ws.write(line, 4 + (pos * 7), score.s_nose)
                ws.write(line, 5 + (pos * 7), score.s_cheek)
                ws.write(line, 6 + (pos * 7), score.s_ear)
                ws.write(line, 7 + (pos * 7), score.s_whiskers)
                ws.write_formula(line, 8 + (pos * 7), f"=SUM({start_col}{line+1}:{end_col}{line+1})")
                ws.write_formula(line, 9 + (pos * 7), f"=AVERAGE({start_col}{line+1}:{end_col}{line+1})")
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

    def create_infofile(self, _path, _files):
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
                        image_file.order = random.randint(0, 5000000)
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
    diversity = models.FloatField(default=0, null=True, blank=True)

    date = models.DateTimeField(blank=True, null=True)
    order = models.IntegerField(default=0, blank=True)

    def calc_similarity(self):
        _params = ["s_eye", "s_nose", "s_cheek", "s_ear", "s_whiskers"]
        n = self.scores.all().distinct("user").count()

        if n >= 2:
            average = {
                "s_eye": self.scores.aggregate(Avg('s_eye')).get('s_eye__avg'),
                "s_nose": self.scores.aggregate(Avg('s_nose')).get('s_nose__avg'),
                "s_cheek": self.scores.aggregate(Avg('s_cheek')).get('s_cheek__avg'),
                "s_ear": self.scores.aggregate(Avg('s_ear')).get('s_ear__avg'),
                "s_whiskers": self.scores.aggregate(Avg('s_whiskers')).get('s_whiskers__avg')
            }

            diversity = 0.
            for score in self.scores.all():
                for val in _params:
                    diversity += abs(getattr(score, val) - average.get(val))

            self.diversity = math.floor(diversity * 100) / 100.0
            self.save()
            return self.diversity
        return 0

    def __str__(self):
        _id = ""
        if os.getenv("DEBUG"):
            _id = f"[{self.pk}] "
        return f"{_id} File: {self.filename} for project {self.project.name}"


class ImageScore(models.Model):
    date = models.DateTimeField(auto_created=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(ImageFile, related_name='scores', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='scores', on_delete=models.CASCADE)
    comment = models.CharField(max_length=255, null=True, default="", blank=True)

    s_eye = models.IntegerField(default=None, null=True, blank=True)
    s_nose = models.IntegerField(default=None, null=True, blank=True)
    s_cheek = models.IntegerField(default=None, null=True, blank=True)
    s_ear = models.IntegerField(default=None, null=True, blank=True)
    s_whiskers = models.IntegerField(default=None, null=True, blank=True)

    def __str__(self):
        _id = ""
        if os.getenv("DEBUG"):
            _id = f"[{self.pk}] "
        return f"{_id} Score: {self.s_eye}{self.s_nose}{self.s_cheek}{self.s_ear}{self.s_whiskers} for '{self.file.filename}' by {self.user.username}"


class Backup(models.Model):
    name = models.CharField(max_length=100, null=False)

    def __str__(self):
        _id = ""
        if os.getenv("DEBUG"):
            _id = f"[{self.pk}] "
        return f"{_id} {self.name}"
