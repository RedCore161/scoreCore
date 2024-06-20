import os

from django.core.management import call_command
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser

from scoring.helper import delete_file, get_path_backup
from scoring.linux import change_file_owner, extract_date_from_filename
from scoring.models import Backup
from scoring.serializers import BackupSerializer
from scoring.views.viewsets.base_viewset import StandardResultsSetPagination
from server.views import RequestSuccess


class BackupViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    serializer_class = BackupSerializer
    queryset = Backup.objects.all().order_by("-id")
    permission_classes = [IsAdminUser]

    @action(detail=False, url_path="readin", methods=["POST"])
    def read_backups(self, request):
        _path = get_path_backup()
        _files = os.listdir(_path)
        for _f in _files:
            try:
                Backup.objects.get(name=_f)
            except Backup.DoesNotExist:
                backup = Backup.objects.create(name=_f)
                backup.date = extract_date_from_filename(_f)
                backup.save()
                change_file_owner(os.path.join(_path, _f))

        return RequestSuccess()

    @action(detail=True, url_path="delete", methods=["POST"])
    def delete_backup(self, request, pk):
        backup = Backup.objects.get(pk=pk)
        delete_file(backup.get_file(), True)
        backup.delete()
        return self.list(request)

    @action(detail=False, url_path="deleteAll", methods=["POST"])
    def delete_all_backups(self, request):
        backups = Backup.objects.all()
        for backup in backups:
            delete_file(backup.get_file(), True)
            backup.delete()

        return self.list(request)

    @action(detail=False, url_path="reload", methods=["POST"])
    def reload_backups(self, request):
        call_command("readbackups")
        return self.list(request)

    @action(detail=False, url_path="create", methods=["POST"])
    def create_backup(self, request):
        call_command("dbbackup")
        call_command("readbackups")
        return self.list(request)

    @action(detail=True, url_path="restore", methods=["POST"])
    def restore_backup(self, request, pk):
        backup = Backup.objects.get(pk=pk)
        call_command("dbrestore", f"--input-file={backup.name}", "--noinput")
        call_command("readbackups")
        return self.list(request)
