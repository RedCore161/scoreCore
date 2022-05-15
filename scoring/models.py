import datetime
import json
import os
import random
import re

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from statsmodels.stats import inter_rater as irr

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
            # df = pd.read_json(data.get("imagefiles"))
            # df.to_csv(f"{os.path.join(_path, _file_template)}.csv", encoding="utf-8", index=False, errors="ignore")

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
        with open(os.path.join(_path, "infofile.txt"), "w") as _file:
            _file.write("\n")
            _file.write("\n")
            _file.write("\n")
            for image in _files:
                if image == "infofile.txt":
                    continue
                _file.write(f"{image}\n")

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
    kappa = models.FloatField(default=None, null=True, blank=True)

    date = models.DateTimeField(blank=True, null=True)
    order = models.IntegerField(default=0, blank=True)

    def calc_kappa(self):
        _params = ["s_eye", "s_nose", "s_cheek", "s_ear", "s_whiskers"]
        n = self.scores.all().distinct("user").count()

        if True:  # n >= 3:
            values = {"0": [self.scores.filter(s_eye=0).count(),
                            self.scores.filter(s_nose=0).count(),
                            self.scores.filter(s_cheek=0).count(),
                            self.scores.filter(s_ear=0).count(),
                            self.scores.filter(s_whiskers=0).count()
                            ],
                      "1": [self.scores.filter(s_eye=1).count(),
                            self.scores.filter(s_nose=1).count(),
                            self.scores.filter(s_cheek=1).count(),
                            self.scores.filter(s_ear=1).count(),
                            self.scores.filter(s_whiskers=1).count()
                            ],
                      "2": [self.scores.filter(s_eye=2).count(),
                            self.scores.filter(s_nose=2).count(),
                            self.scores.filter(s_cheek=2).count(),
                            self.scores.filter(s_ear=2).count(),
                            self.scores.filter(s_whiskers=2).count()
                            ],
                      "None": [self.scores.filter(s_eye__isnull=True).count(),
                               self.scores.filter(s_nose__isnull=True).count(),
                               self.scores.filter(s_cheek__isnull=True).count(),
                               self.scores.filter(s_ear__isnull=True).count(),
                               self.scores.filter(s_whiskers__isnull=True).count()
                               ],
                      }

            values2 = {
                "s_eye": [
                    self.scores.filter(s_eye=0).count(),
                    self.scores.filter(s_eye=1).count(),
                    self.scores.filter(s_eye=2).count(),
                    self.scores.filter(s_eye__isnull=True).count(),
                ],
                "s_nose": [
                    self.scores.filter(s_nose=0).count(),
                    self.scores.filter(s_nose=1).count(),
                    self.scores.filter(s_nose=2).count(),
                    self.scores.filter(s_nose__isnull=True).count(),
                ],
                "s_cheek": [
                    self.scores.filter(s_cheek=0).count(),
                    self.scores.filter(s_cheek=1).count(),
                    self.scores.filter(s_cheek=2).count(),
                    self.scores.filter(s_cheek__isnull=True).count(),
                ],
                "s_ear": [
                    self.scores.filter(s_ear=0).count(),
                    self.scores.filter(s_ear=1).count(),
                    self.scores.filter(s_ear=2).count(),
                    self.scores.filter(s_ear__isnull=True).count()
                ],
                "s_whiskers": [
                    self.scores.filter(s_whiskers=0).count(),
                    self.scores.filter(s_whiskers=1).count(),
                    self.scores.filter(s_whiskers=2).count(),
                    self.scores.filter(s_whiskers__isnull=True).count()
                ],
            }
            # final = [values.get(val) for val in _params]
            final = [values.get(val) for val in ["0", "1", "2", "None"]]

            agg = irr.aggregate_raters(final)
            kappa = irr.fleiss_kappa(agg[0], method='fleiss')
            print("RESULT", kappa, final)
            self.kappa = kappa
            self.save()

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
