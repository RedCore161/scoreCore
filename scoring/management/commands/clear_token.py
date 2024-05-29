from django.core.management.base import BaseCommand
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from scoring.helper import dlog


class Command(BaseCommand):
    help = "Clear Tokens"

    def handle(self, *args, **options):
        BlacklistedToken.objects.all().delete()
        OutstandingToken.objects.all().delete()
        dlog("Cleared Token")
