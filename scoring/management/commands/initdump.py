import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from scoring.models import Project
from server.settings import BASE_DIR


class Command(BaseCommand):
    help = 'Fills in initial test data'

    def handle(self, *args, **options):

        username = os.getenv("DJANGO_SUPERUSER_USERNAME")

        if username:
            user = get_user_model().objects.get(username=username)

            projects = {"wolter": {"image_dir": "Frames_Wolter"},
                        "Einzel-Training 1": {"image_dir": "Einzel_Training1", "check": True},
                        "Einzel-Training 2": {"image_dir": "Einzel_Training2", "check": True}
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
                project.users.add(user)
                project.save()
