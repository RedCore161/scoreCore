import os

from django.contrib.auth.models import User
from rest_framework import serializers

from scoring.models import Project, ImageScore, ImageFile


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username"]


class ProjectSerializer(serializers.ModelSerializer):

    imagesTotal = serializers.SerializerMethodField("get_total_images_count")
    uselessCount = serializers.SerializerMethodField("get_useless_count")
    scoresCount = serializers.SerializerMethodField("get_scores_count")
    scoresOwn = serializers.SerializerMethodField("get_own_scores_count")

    class Meta:
        model = Project
        fields = "__all__"

    @staticmethod
    def get_total_images_count(obj: Project):
        return obj.files.exclude(useless=True).count()

    @staticmethod
    def get_useless_count(obj: Project):
        return obj.files.filter(useless=True, hidden=False).count()

    @staticmethod
    def get_scores_count(obj: Project):
        return obj.scores.exclude(file__useless=True).count()

    def get_own_scores_count(self, obj: Project):
        user = User.objects.get(pk=self.context.get("user"))
        return obj.scores.exclude(file__useless=True).filter(user=user).count()


class ImageScoreSerializer(serializers.ModelSerializer):

    file_name = serializers.SerializerMethodField("get_filename")
    full_path = serializers.SerializerMethodField("get_full_path")
    user = UserSerializer(read_only=True)

    class Meta:
        model = ImageScore
        exclude = ["date", "project", "file"]

    @staticmethod
    def get_filename(obj: ImageScore):
        return obj.file.filename

    @staticmethod
    def get_full_path(obj: ImageScore):
        return obj.file.path.replace("\\", "/") + "/" + obj.file.filename


class ImageFileSerializer(serializers.ModelSerializer):
    scores = ImageScoreSerializer(many=True, read_only=True)
    rel_path = serializers.SerializerMethodField("get_rel_path")

    class Meta:
        model = ImageFile
        fields = "__all__"

    @staticmethod
    def get_rel_path(obj: ImageFile):
        # remove '../media/'
        index = obj.path.find("media")
        return obj.path[index+6:]


# class ProductSerializer(serializers.ModelSerializer):
#     product = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Product
#         fields = "__all__"
#
#     @staticmethod
#     def get_product(obj: Product):
#         return obj.get_product_name()

