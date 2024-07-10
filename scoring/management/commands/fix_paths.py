from django.core.management.base import BaseCommand
from scoring.helper import ilog
from scoring.models import ImageFile


class Command(BaseCommand):
    help = "Fixxing"

    def handle(self, *args, **options):

        images = ImageFile.objects.all()
        for image in images:
            image.fix_path()

        ilog(f"Fixxing paths", tag="[DONE]")
