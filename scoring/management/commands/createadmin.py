import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from server.settings import BASE_DIR


class Command(BaseCommand):
    help = 'Create Admin-Django user from environment'

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

            # # Create a Token for watch-dog
            # _user = user.objects.get(username=username)
            # token, _ = Token.objects.get_or_create(user=_user)
            # with open(os.path.join(BASE_DIR, "token"), 'w') as f:
            #     f.write(token.key)
