from django.core.management.base import BaseCommand
from scoring.helper import ilog, elog
from scoring.models import ImageFile
from server.settings import IS_PRODUCTION


class Command(BaseCommand):
    help = "Resetting all imagefiles"

    def handle(self, *args, **options):
        if IS_PRODUCTION:
            elog("Can't reset in productive settings... Exiting!")
            return

        for im in ImageFile.objects.all():
            im.stddev = 0
            im.data = {}
            im.save()
            im.calc_std_dev()

        ilog("Reset data", tag="[DONE]")
