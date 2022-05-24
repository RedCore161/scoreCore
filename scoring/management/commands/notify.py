from django.core.management import call_command
from django.core.management.base import BaseCommand

from scoring.helper import ilog


class Command(BaseCommand):
    help = 'Notify django about something'

    def add_arguments(self, parser):

        parser.add_argument(
            '-cb', '--created-backup', default=0,
            type=int, choices=[0, 1],
            help='',
        )

    def handle(self, *args, **options):

        created_backup = options.get("created_backup")
        if created_backup:
            ilog("New Backup was created!", tag="[NOTIFY]")
            call_command("readbackups")





