import os

from django.core.management import call_command
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser

from scoring.basics import parse_boolean
from scoring.helper import delete_file, get_path_backup
from scoring.linux import extract_date_from_filename
from scoring.models import ImageFile
from scoring.serializers import ImageFileSerializer
from scoring.views.viewsets.base_viewset import StandardResultsSetPagination
from server.views import RequestSuccess


def find_duplicates_from_map(hash_dict, image_files):
    """
    Finds and prints all duplicate hashes in the provided dictionary.
    The dictionary should have folder paths as keys and lists of hashes as values.
    """
    # Create a reverse lookup dictionary to map hashes to their corresponding file paths
    reverse_lookup = {}
    duplicates = []

    for folder, hashes in hash_dict.items():
        # print("XXX", folder, "\n", hashes, "\n")
        for file_hash in hashes:
            if file_hash in reverse_lookup:
                reverse_lookup[file_hash].append(folder)
            else:
                reverse_lookup[file_hash] = [folder]

    for file_hash, folders in reverse_lookup.items():
        if len(folders) > 1:
            # duplicates.append({file_hash: {"files": [os.path.join(img.get_rel_path(), img.filename) for img in image_files.filter(raw_hash=file_hash)]}})

            files = []
            for img in image_files.filter(raw_hash=file_hash):
                _source = img.get_video_source()
                if _source:
                    files.append({"path": f"{img.get_rel_path()}/{img.filename}", "source": _source, "project": img.project.name})
            duplicates.append({file_hash: files})

    return duplicates


class ImageFileViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    serializer_class = ImageFileSerializer
    queryset = ImageFile.objects.all().order_by("-id")
    permission_classes = [IsAdminUser]

    @staticmethod
    def create_hashes_dict(image_files):
        _dict = {}
        for image_file in image_files:
            pos = image_file.path.rindex("/")
            # _dir = image_file.path[:pos]
            _dir = image_file.path
            _hashes = _dict.get(_dir, [])
            _hashes.append(image_file.raw_hash)
            _dict.update({_dir: _hashes})
        return _dict

    @action(detail=False, url_path="recalc", methods=["POST"])
    def recalc_hashes(self, request):
        image_files = self.get_queryset()
        for image_file in image_files:
            image_file.calc_hash()
            image_file.save()
        return RequestSuccess()

    @action(detail=False, url_path="hashes/list", methods=["GET"])
    def list_hashes(self, request):
        image_files = self.get_queryset()

        _dict = self.create_hashes_dict(image_files)

        return RequestSuccess(_dict)

    @action(detail=False, url_path="duplicates", methods=["GET"])
    def find_duplicates(self, request):
        image_files = self.get_queryset()

        _dict = self.create_hashes_dict(image_files)
        _dups = find_duplicates_from_map(_dict, image_files)
        return RequestSuccess({"data": _dups})
