import random

from django.db.models import Count
from django.utils import timezone
from rest_framework.response import Response

from scoring.helper import elog, dlog, ilog
from scoring.models import ImageFile, ImageScore, Project
from scoring.serializers import ImageFileSerializer
from server.views import RequestSuccess


class ViewSetCreateModel(object):

    @staticmethod
    def create_or_update_imagescore(pk, user, data, comment="") -> bool:

        def replace_none(_str):
            if _str == "X" or _str == '':
                return None
            return _str

        dlog(f"create_or_update_imagescore | {data=}, {comment=}")
        image_file = ImageFile.objects.get(pk=pk)

        score, created = ImageScore.objects.get_or_create(user=user,
                                                          project=image_file.project,
                                                          file=image_file)

        scoring_fields = image_file.project.features.all().values_list("name", flat=True)
        _i = 0

        score.data = dict(zip(scoring_fields, data))
        score.data = {k: replace_none(v) for k, v in zip(scoring_fields, data)}
        # score.s_eye = replace_none(data[0])
        # score.s_nose = replace_none(data[1])
        # score.s_cheek = replace_none(data[2])
        # score.s_ear = replace_none(data[3])
        # score.s_whiskers = replace_none(data[4])
        image_file.calc_varianz()

        if created:
            score.comment = comment
            score.date = timezone.now()

        score.save()
        score.check_completed()

        return created

    @staticmethod
    def get_next_image(pk, user, file=None) -> dict:
        project = Project.objects.get(pk=pk)

        base_request = ImageFile.objects.filter(project=pk)\
                                        .exclude(hidden=True)\
                                        .exclude(useless=True)\
                                        .exclude(scores__user=user)\
                                        .annotate(scores_ratio=Count("scores"))

        available_images = len(base_request)

        if available_images == 0:
            return {"files_left": 0}

        self_scored = ImageFile.objects.filter(project=pk, scores__user=user)\
                                       .exclude(hidden=True)\
                                       .exclude(useless=True).count()

        scores_ratio = base_request.order_by("scores_ratio")[0].scores_ratio

        images = base_request.filter(scores_ratio=scores_ratio)

        count = project.wanted_scores_per_user - self_scored
        if count > available_images:
            count = available_images

        if count == 0:
            return {"files_left": count, "scores_ratio": scores_ratio}

        if file:
            image_file = ImageFile.objects.get(pk=file, project=pk)
            serializer = ImageFileSerializer(image_file, read_only=True)
            return {"files_left": count, "image": serializer.data, "scores_ratio": scores_ratio}

        if len(images):
            rnd = random.randint(0, len(images) - 1)
            serializer = ImageFileSerializer(images[rnd])
            return {"files_left": count, "image": serializer.data, "scores_ratio": scores_ratio, "random": rnd}

        return {"files_left": 0, "scores_ratio": scores_ratio}
