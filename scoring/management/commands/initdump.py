import json
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from scoring.helper import random_string, get_path_setup, okaylog, ilog, elog
from scoring.models import Project


class Command(BaseCommand):
    # OUTDATED
    help = "Fills in initial test data"

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")

        if username:
            root = get_user_model().objects.get(username=username)
        else:
            root = None

        _path = get_path_setup("users.json")
        if not os.path.exists(_path):
            elog("No 'users.json' in media/setup... Stopping!")
            return

        with open(get_path_setup("users.json"), "r") as _file:
            _users = json.load(_file)

            for _user in _users:
                user, created = User.objects.get_or_create(username=_user.get("username"), email=_user.get("email"))

                if created:
                    user.set_password(_user.get("password", random_string(4, 4)))
                    user.first_name = _user.get("firstName")
                    user.last_name = _user.get("lastName")
                    if _user.get("isStaff"):
                        user.is_staff = _user.get("isStaff")
                    user.save()

        users = User.objects.all()
        projects = {
                    "Einzel-Demo": {"image_dir": "Einzel-Demo", "check": True, "allUsers": True},
                    }

        for name in projects:
            ilog("Project", name, "...\n")
            project, created = Project.objects.get_or_create(name=name, image_dir=projects[name].get("image_dir"))

            if projects[name].get("createScript", False):
                project.create_script()
            if projects[name].get("check", False):
                project.check_create_infofiles()
            result = project.read_images(False)

            if created:
                okaylog("Created Project!", result, project)
                if projects[name].get("allUsers", False):
                    for _user in users:
                        project.users.add(_user)

            if root:
                project.users.add(root)

            project.save()
