import random

from django.db.models import Count
from django.utils import timezone

from scoring.helper import dlog
from scoring.models import ImageFile, ImageScore, Project
from scoring.serializers import ImageFileSerializer, ImageScoreSerializer


class ViewSetCreateModel(object):

    @staticmethod
    def create_or_update_imagescore(pk, user, scoring_fields, data, comment="") -> bool:

        dlog(f"create_or_update_imagescore | {data=}, {comment=}")
        image_file = ImageFile.objects.get(pk=pk)

        score, created = ImageScore.objects.get_or_create(user=user,
                                                          project=image_file.project,
                                                          file=image_file)

        _zip = zip(scoring_fields, data)
        score.data = dict(_zip)

        if created:
            score.comment = comment

        if score.comment != comment:
            score.comment = comment

        score.date = timezone.now()
        score.save()

        if score.check_completed():
            image_file.calc_variance()

        return created

    @staticmethod
    def get_next_image(pk, user, file=None) -> dict:
        project = Project.objects.get(pk=pk)

        base_request = ImageFile.objects.filter(project=pk) \
            .exclude(hidden=True) \
            .exclude(useless=True) \
            .exclude(scores__user=user, scores__is_completed=True) \
            .annotate(scores_ratio=Count("scores"))

        available_images = len(base_request)

        if available_images == 0:
            return {"files_left": 0}

        self_scored = ImageFile.objects.filter(project=pk, scores__user=user, scores__is_completed=True) \
            .exclude(hidden=True) \
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
            score = ImageScore.objects.filter(user=user, file=image_file)
            serializer_file = ImageFileSerializer(image_file, read_only=True)
            data = {"files_left": count, "image": serializer_file.data, "scores_ratio": scores_ratio}

            if score:
                serializer_score = ImageScoreSerializer(score[0], read_only=True)
                data.update({"score": serializer_score.data})
            return data

        if len(images):
            rnd = random.randint(0, len(images) - 1)
            serializer_file = ImageFileSerializer(images[rnd])
            return {"files_left": count, "image": serializer_file.data, "scores_ratio": scores_ratio, "random": rnd}

        return {"files_left": 0, "scores_ratio": scores_ratio}
