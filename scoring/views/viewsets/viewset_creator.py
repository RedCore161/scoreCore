import random

from django.db.models import Count
from django.utils import timezone

from scoring.basics import parse_boolean
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
    def get_next_image(request, pk) -> dict:

        user = request.user
        file = request.GET.get("file")
        autoload = parse_boolean(request.GET.get("autoload", True))
        project = Project.objects.get(pk=pk)

        base_request = ImageFile.objects.filter(project=pk) \
            .exclude(hidden=True) \
            .exclude(useless=True)

        done_request = base_request.exclude(scores__user=user, scores__is_completed=False) \
                                   .annotate(scores_ratio=Count("scores"))

        open_request = base_request.exclude(scores__user=user, scores__is_completed=True)
        open_scores = open_request.count()
        files_request = ImageFile.objects.filter(project=pk, scores__user=user) \
            .exclude(hidden=True) \
            .exclude(useless=True)
        score_started = files_request.count()
        score_finished = files_request.filter(scores__user=user, scores__is_completed=True).count()
        image_files = len(base_request)
        count = project.wanted_scores_per_user - max(score_started, score_finished)

        dlog(f"done={len(done_request)}, {file=}, {autoload=}, {count=}, {open_scores=}, {score_started=}, {score_finished=}, {image_files=}")
        response = {"files_left": image_files - score_started,
                   "image_files": image_files,
                   "count": count,
                   "score_desired": project.wanted_scores_per_user,
                   "score_started": score_started,
                   "score_finished": score_finished}

        if len(done_request) > 0:
            scores_ratio = done_request.order_by("scores_ratio")[0].scores_ratio
            response.update({"scores_ratio": scores_ratio})
            images = done_request.filter(scores_ratio=scores_ratio)
        else:
            images = []

        if file:
            image_file = ImageFile.objects.get(pk=file, project=pk)
        elif autoload:
            req = ImageScore.objects.filter(project=pk, user=user, is_completed=False)
            image_score = random.choice(req) if len(req) else None
            image_file = image_score.file if image_score else None
        else:
            image_file = None

        if image_file:
            score = ImageScore.objects.get(user=user, file=image_file)
            serializer_file = ImageFileSerializer(image_file, read_only=True)
            response.update({"image": serializer_file.data})

            if score:
                serializer_score = ImageScoreSerializer(score, read_only=True)
                response.update({"score": serializer_score.data})

            print("XXX", response)
            return response

        if count <= 0:
            return response

        if len(images):
            rnd = random.randint(0, len(images) - 1)
            _image_file = images[rnd]
            serializer_file = ImageFileSerializer(_image_file)
            score = ImageScore.objects.filter(user=user, file=_image_file)
            response.update({"image": serializer_file.data,
                            "random": rnd})

            if len(score):
                serializer_score = ImageScoreSerializer(score[0], read_only=True)
                response.update({"score": serializer_score.data})

        return response
