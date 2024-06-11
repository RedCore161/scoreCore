from django.core.management.base import BaseCommand
from scoring.helper import ilog, elog
from server.settings import IS_PRODUCTION


class Command(BaseCommand):
    help = "Resetting all passwords"
    reset = "resetted_pw"

    def handle(self, *args, **options):
        from django.contrib.auth.models import User
        if IS_PRODUCTION:
            elog("Can't reset pws in productive settings... Exiting!")
            return

        users = User.objects.all()
        for user in users:
            user.set_password(self.reset)
            user.save()

        ilog(f"Reset pws to '{self.reset}'")
