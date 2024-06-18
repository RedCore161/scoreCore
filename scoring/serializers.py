from django.contrib.auth.models import User
from django.contrib.auth.password_validation import UserAttributeSimilarityValidator, \
    MinimumLengthValidator
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from scoring.models import Project, ImageScore, ImageFile, Backup, ScoreFeature, TimestampField
from scoring.validators import NumberValidator


class MinimalUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "username")


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "username", "email", "last_login", "is_superuser", "is_staff", "is_active")


class PasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True,
                                         validators=[UserAttributeSimilarityValidator,
                                                     MinimumLengthValidator,
                                                     NumberValidator,
                                                     # TODO CommonPasswordValidator(get_path_setup("common-passwords.txt.gz")),
                                                     ])

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class ScoreFeaturesSerializer(serializers.ModelSerializer):
    clazz = serializers.SerializerMethodField("get_clazz_name")

    class Meta:
        model = ScoreFeature
        exclude = ["project"]

    @staticmethod
    def get_clazz_name(_):
        return "scorefeature"


class ProjectSerializer(serializers.ModelSerializer):
    clazz = serializers.SerializerMethodField("get_clazz_name")
    isFinished = serializers.SerializerMethodField("get_is_finished")
    evaluations = serializers.SerializerMethodField("get_evaluations")
    features = serializers.SerializerMethodField("get_features")
    users = serializers.SerializerMethodField("get_users")
    data = serializers.SerializerMethodField("get_data")

    class Meta:
        model = Project
        fields = "__all__"

    @staticmethod
    def get_clazz_name(_):
        return "project"

    @staticmethod
    def get_is_finished(project: Project):
        return project.is_finished()

    def get_data(self, project: Project):
        _user = self.context.get("user")
        return project.get_data(_user)

    @staticmethod
    def get_evaluations(project: Project):
        return project.get_existing_evaluations()

    @staticmethod
    def get_features(project: Project):
        return ScoreFeaturesSerializer(project.features.all(), many=True).data

    @staticmethod
    def get_users(project: Project):
        return MinimalUserSerializer(project.users.all(), many=True).data


class ImageScoreSerializer(serializers.ModelSerializer):
    clazz = serializers.SerializerMethodField("get_clazz_name")
    file_name = serializers.SerializerMethodField("get_filename")
    full_path = serializers.SerializerMethodField("get_full_path")
    timestamp = TimestampField(source="date")
    user = MinimalUserSerializer(read_only=True)
    # project = ProjectSerializer()

    class Meta:
        model = ImageScore
        exclude = ["project"]

    @staticmethod
    def get_clazz_name(_):
        return "imagescore"

    @staticmethod
    def get_filename(score: ImageScore):
        return score.file.filename

    @staticmethod
    def get_full_path(score: ImageScore):
        return score.file.path.replace("\\", "/") + "/" + score.file.filename


class ImageFileSerializer(serializers.ModelSerializer):
    clazz = serializers.SerializerMethodField("get_clazz_name")
    scores = ImageScoreSerializer(many=True, read_only=True)

    class Meta:
        model = ImageFile
        fields = "__all__"

    @staticmethod
    def get_clazz_name(_):
        return "imagefile"


class BackupSerializer(serializers.ModelSerializer):
    clazz = serializers.SerializerMethodField("get_clazz_name")

    class Meta:
        model = Backup
        fields = "__all__"

    @staticmethod
    def get_clazz_name(_):
        return "backup"


class RedcoreTokenObtainPairSerializer(TokenObtainPairSerializer):

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["username"] = user.username
        token["is_staff"] = user.is_staff
        token["is_superuser"] = user.is_superuser
        token["is_demo"] = user.username in ["demo", "unit_tests"]
        # ...

        return token
