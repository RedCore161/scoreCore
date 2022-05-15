import os

from django.contrib.auth.models import User
from rest_auth.models import TokenModel
from rest_framework import serializers

from scoring.models import Project, ImageScore, ImageFile, Backup


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "username")


class TokenSerializer(serializers.ModelSerializer):
    """
    Serializer for Token model.
    """

    is_staff = serializers.SerializerMethodField("get_is_staff")
    is_superuser = serializers.SerializerMethodField("get_is_superuser")
    is_active = serializers.SerializerMethodField("get_is_active")

    class Meta:
        model = TokenModel
        fields = ("key", "is_staff", "is_superuser", "is_active")

    @staticmethod
    def get_is_staff(obj: TokenModel):
        return obj.user.is_staff

    @staticmethod
    def get_is_superuser(obj: TokenModel):
        return obj.user.is_superuser

    @staticmethod
    def get_is_active(obj: TokenModel):
        return obj.user.is_active


class ProjectSerializer(serializers.ModelSerializer):
    clazz = serializers.SerializerMethodField("get_clazz_name")
    imagesTotal = serializers.SerializerMethodField("get_total_images_count")
    uselessCount = serializers.SerializerMethodField("get_useless_count")
    scoresCount = serializers.SerializerMethodField("get_scores_count")
    scoresOwn = serializers.SerializerMethodField("get_own_scores_count")
    evaluations = serializers.SerializerMethodField("get_evaluations")

    class Meta:
        model = Project
        fields = "__all__"

    @staticmethod
    def get_clazz_name(obj: Project):
        return "project"

    @staticmethod
    def get_total_images_count(obj: Project):
        return obj.files.exclude(useless=True).count()

    @staticmethod
    def get_useless_count(obj: Project):
        return obj.files.filter(useless=True, hidden=False).count()

    @staticmethod
    def get_scores_count(obj: Project):
        return obj.scores.exclude(file__useless=True).count()

    @staticmethod
    def get_evaluations(obj: Project):
        return obj.get_existing_evaluations()

    def get_own_scores_count(self, obj: Project):
        if not self.context.get("user"):
            return 0
        user = User.objects.get(pk=self.context.get("user"))
        return obj.scores.exclude(file__useless=True).filter(user=user).count()


class ImageScoreSerializer(serializers.ModelSerializer):
    clazz = serializers.SerializerMethodField("get_clazz_name")
    file_name = serializers.SerializerMethodField("get_filename")
    full_path = serializers.SerializerMethodField("get_full_path")
    user = UserSerializer(read_only=True)

    class Meta:
        model = ImageScore
        exclude = ("date", "project", "file")

    @staticmethod
    def get_clazz_name(obj: ImageScore):
        return "imagescore"

    @staticmethod
    def get_filename(obj: ImageScore):
        return obj.file.filename

    @staticmethod
    def get_full_path(obj: ImageScore):
        return obj.file.path.replace("\\", "/") + "/" + obj.file.filename


class ImageFileSerializer(serializers.ModelSerializer):
    clazz = serializers.SerializerMethodField("get_clazz_name")
    scores = ImageScoreSerializer(many=True, read_only=True)
    rel_path = serializers.SerializerMethodField("get_rel_path")

    class Meta:
        model = ImageFile
        fields = "__all__"

    @staticmethod
    def get_clazz_name(obj: ImageFile):
        return "imagefile"

    @staticmethod
    def get_rel_path(obj: ImageFile):
        # remove '../media/'
        index = obj.path.find("media")
        return obj.path[index+6:]


class BackupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Backup
        fields = "__all__"
