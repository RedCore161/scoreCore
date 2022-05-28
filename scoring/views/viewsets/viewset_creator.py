import math
import random

from django.db.models import Count
from django.utils import timezone
from rest_framework.response import Response

from scoring.helper import okaylog
from scoring.models import ImageFile, ImageScore, Project
from scoring.serializers import ImageFileSerializer
from server.views import RequestSuccess


class ViewSetCreateModel(object):

    @staticmethod
    def create_imagescore(pk, user, data, comment="") -> bool:

        def replace_none(_str):
            if _str == "X":
                return None
            return _str

        image_file = ImageFile.objects.get(pk=pk)

        score, created = ImageScore.objects.get_or_create(user=user,
                                                          project=image_file.project,
                                                          file=image_file,
                                                          s_eye=replace_none(data[0]),
                                                          s_nose=replace_none(data[1]),
                                                          s_cheek=replace_none(data[2]),
                                                          s_ear=replace_none(data[3]),
                                                          s_whiskers=replace_none(data[4]))

        if created:
            score.comment = comment,
            score.date = timezone.now()
            score.save()

            image_file.calc_varianz()

        return created

    @staticmethod
    def get_next_image(pk, user) -> Response:
        project = Project.objects.get(pk=pk)

        base_request = ImageFile.objects.filter(project=pk) \
            .exclude(hidden=True) \
            .exclude(useless=True) \
            .exclude(scores__user=user) \
            .annotate(scores_ratio=Count('scores'))

        self_scored = ImageFile.objects.filter(project=pk, scores__user=user) \
            .exclude(hidden=True) \
            .exclude(useless=True).count()

        scores_ratio = base_request.order_by("scores_ratio")[0].scores_ratio

        images = base_request.filter(scores_ratio=scores_ratio)

        count = project.wanted_scores_per_user - self_scored

        # okaylog("scores_ratio", scores_ratio)
        # okaylog("project.scores.count", project.scores.count())
        # okaylog("images", len(images))
        # okaylog("self_scored", self_scored)
        # okaylog("project.wanted_scores_per_user", project.wanted_scores_per_user, "\n")

        if count == 0:
            return RequestSuccess({"files_left": count, "scores_ratio": scores_ratio})

        if len(images):
            serializer = ImageFileSerializer(images, many=True)
            rnd = random.randint(0, len(images) - 1)
            return RequestSuccess({"files_left": count, "image": serializer.data[rnd],
                                   "scores_ratio": scores_ratio, "random": rnd})

        return RequestSuccess({"files_left": 0, "scores_ratio": scores_ratio})
