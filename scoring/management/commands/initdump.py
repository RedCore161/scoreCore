import json
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from scoring.helper import random_string, get_setup_path
from scoring.models import Project
from server.settings import BASE_DIR


class Command(BaseCommand):
    help = 'Fills in initial test data'

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")

        if username:
            root = get_user_model().objects.get(username=username)
        else:
            root = None

        with open(os.path.join(get_setup_path(), "users.json"), "r") as _file:
            _users = json.load(_file)

            for _user in _users:
                user, created = User.objects.get_or_create(username=_user.get("username"),
                                                           email=_user.get("email")
                                                           )

                if created:
                    user.password = random_string(4, 4)
                    user.first_name = _user.get("firstName")
                    user.last_name = _user.get("lastName")
                    if _user.get("isStaff"):
                        user.is_staff = _user.get("isStaff")
                    user.save()

        users = User.objects.all()
        projects = {"wolter_demo": {"image_dir": "Frames_Wolter"},
                    "Einzel-Training 1": {"image_dir": "Einzel_Training1", "check": True, "allUsers": True},
                    "Einzel-Training 2": {"image_dir": "Einzel_Training2", "check": True, "allUsers": True}
                    }

        for name in projects:
            print("Project", name, "...\n")
            project, created = Project.objects.get_or_create(name=name, image_dir=projects[name].get("image_dir"))

            if projects[name].get("createScript", False):
                project.create_script()
            if projects[name].get("check", False):
                project.check_create_infofiles()
            result = project.read_images()

            if created:
                print("Created Project!", result, project)
                if projects[name].get("allUsers", False):
                    for _user in users:
                        project.users.add(_user)

            if root:
                project.users.add(root)

            project.save()
