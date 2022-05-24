from django.core.management.base import BaseCommand
from scoring.views.viewsets.backup_viewset import BackupViewSet


class Command(BaseCommand):
    help = 'Reads all backup-files as models'

    def handle(self, *args, **options):
        BackupViewSet().read_backups(None)



