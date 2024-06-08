import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from scoring.helper import save_check_dir
from server.settings import DEFAULT_DIRS


class Command(BaseCommand):
    help = "Create Admin-Django user from environment"

    def handle(self, *args, **options):

        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        pw = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        mail = os.getenv("DJANGO_SUPERUSER_EMAIL")

        if username and pw and mail:
            user = get_user_model()
            try:
                user.objects.get(username=username)
            except User.DoesNotExist:
                user.objects.create_superuser(username, mail, pw)
                self.stdout.write(self.style.SUCCESS('Created Admin!'))

        for _dir in DEFAULT_DIRS.keys():
            save_check_dir(_dir)

