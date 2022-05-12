import os

from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    name = models.CharField(max_length=100, null=False)
    image_dir = models.CharField(max_length=500, null=True, blank=True)
    users = models.ManyToManyField(User)

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
    date = models.DateTimeField(blank=True, null=True)
    order = models.IntegerField(default=0, blank=True)

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
    s_whiskas = models.IntegerField(default=None, null=True, blank=True)

    def __str__(self):
        _id = ""
        if os.getenv("DEBUG"):
            _id = f"[{self.pk}] "
        return f"{_id} Score: {self.s_eye}{self.s_nose}{self.s_cheek}{self.s_ear}{self.s_whiskas} for '{self.file.filename}' by {self.user.username}"
