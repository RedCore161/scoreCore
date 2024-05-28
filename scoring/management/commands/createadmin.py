import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from scoring.helper import save_check_dir
from server.settings import BACKUP_DIR, SETUP_DIR, UPLOAD_DIR, EXPORT_DIR, LOGS_DIR, PROJECT_DIR


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

        save_check_dir(BACKUP_DIR)
        save_check_dir(SETUP_DIR)
        save_check_dir(UPLOAD_DIR)
        save_check_dir(EXPORT_DIR)
        save_check_dir(LOGS_DIR)
        save_check_dir(PROJECT_DIR)
