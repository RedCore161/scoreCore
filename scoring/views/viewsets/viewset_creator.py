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
            .exclude(useless=True)

        done_request = base_request.exclude(scores__user=user, scores__is_completed=False) \
                                   .annotate(scores_ratio=Count("scores"))

        open_request = base_request.exclude(scores__user=user, scores__is_completed=True)
        open_scores = open_request.count()
        self_scored = ImageFile.objects.filter(project=pk, scores__user=user, scores__is_completed=True) \
            .exclude(hidden=True) \
            .exclude(useless=True).count()
        image_files = len(base_request)

        #print("==> Done", len(done_request), "open_scores:", open_scores, "self_scored:", self_scored, "image_files:", image_files)

        scores_ratio = done_request.order_by("scores_ratio")[0].scores_ratio
        respond = {"files_left": image_files - self_scored,
                   "image_files": image_files,
                   "scores_ratio": scores_ratio}

        if self_scored == image_files:
            return respond

        images = done_request.filter(scores_ratio=scores_ratio)

        print("scores_ratio", scores_ratio)
        print("images", images)

        count = project.wanted_scores_per_user - open_scores
        if count > open_scores:
            count = open_scores

        if file:
            image_file = ImageFile.objects.get(pk=file, project=pk)
            score = ImageScore.objects.filter(user=user, file=image_file)
            serializer_file = ImageFileSerializer(image_file, read_only=True)
            data = respond | {"image": serializer_file.data,
                              "count": count}

            if score:
                serializer_score = ImageScoreSerializer(score[0], read_only=True)
                data.update({"score": serializer_score.data})
            return data

        if len(images):
            rnd = random.randint(0, len(images) - 1)
            _image_file = images[rnd]
            print("_image_file", _image_file)
            serializer_file = ImageFileSerializer(_image_file)
            score = ImageScore.objects.filter(user=user, file=_image_file)
            _result = respond | {"image": serializer_file.data,
                                 "random": rnd}
            print("_result", _result)

            if len(score):
                serializer_score = ImageScoreSerializer(score[0], read_only=True)
                return _result | {"score": serializer_score.data}
            return _result

        return respond
