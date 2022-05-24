import random

from django.db.models import Count
from django.utils import timezone
from rest_framework.response import Response

from scoring.models import ImageFile, ImageScore, Project
from scoring.serializers import ImageFileSerializer
from server.views import RequestSuccess


class ViewSetCreateModel(object):

    @staticmethod
    def create_imagescore(pk, user, eye, nose, cheek, ear, whiskers, comment=""):
        image_file = ImageFile.objects.get(pk=pk)

        score = ImageScore.objects.create(user=user,
                                          project=image_file.project,
                                          file=image_file,
                                          s_eye=eye,
                                          s_nose=nose,
                                          s_cheek=cheek,
                                          s_ear=ear,
                                          s_whiskers=whiskers,
                                          comment=comment,
                                          date=timezone.now())
        score.save()

        image_file.calc_varianz()


    @staticmethod
    def get_images(pk, user) -> Response:
        project = Project.objects.get(pk=pk)

        base_request = ImageFile.objects.filter(project=pk) \
            .exclude(hidden=True) \
            .exclude(useless=True) \
            .exclude(scores__user=user) \
            .annotate(scores_min=Count('scores'))

        min_count = base_request.order_by("scores_min")[0].scores_min

        images = base_request.filter(scores_min=min_count)

        scored = ImageFile.objects.filter(project=pk, scores__user=user) \
            .exclude(hidden=True) \
            .exclude(useless=True).count()

        serializer = ImageFileSerializer(images, many=True)
        count = project.wanted_scores_per_user - scored

        if count == 0:
            return RequestSuccess({"files_left": count})

        if len(images):
            rnd = random.randint(0, len(images) - 1)
            return RequestSuccess({"files_left": count, "image": serializer.data[rnd], "random": rnd})
        return RequestSuccess({"files_left": count})
