import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from scoring.models import Project


class Command(BaseCommand):
    help = 'Fills in initial test data'

    def handle(self, *args, **options):

        username = os.getenv("DJANGO_SUPERUSER_USERNAME")

        if username:
            user = get_user_model().objects.get(username=username)

            projects = ["wolter", "wilzopolski"]

            project, created = Project.objects.get_or_create(name=projects[0], image_dir="Frames_Wolter")
            project.users.add(user)
            project.save()

            project, created = Project.objects.get_or_create(name=projects[1])
            project.users.add(user)
            project.save()
