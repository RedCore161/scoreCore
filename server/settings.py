import os
from datetime import timedelta

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / "subdir".
from scoring.basics import parse_boolean, parse_int
from server.read_env import read_env

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

ENV_FILE_PATH = os.path.join(BASE_DIR, "django.env")

read_env(ENV_FILE_PATH)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")
# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = os.getenv("DEBUG") == "1"
DEBUG_PROPAGATE_EXCEPTIONS = True

INTERNAL_IPS = ["127.0.0.1"]

ALLOWED_HOSTS = [os.getenv("DJANGO_ALLOWED_HOSTS")]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",

    "dbbackup",

    "corsheaders",

    "django_celery_results",
    "channels",

    "scoring",
]

CELERY_RESULT_EXTENDED = True
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SOFT_TIME_LIMIT = None
CELERY_TASK_TIME_LIMIT = None

outtime = 60 * 60 * 4

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
}

REST_FRAMEWORK = {
    "DATETIME_FORMAT": "%d.%m.%Y, %H:%M:%S",

    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ]
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": os.getenv("SIGNING_KEY", None),
    "VERIFYING_KEY": os.getenv("VERIFYING_KEY", None),
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",

    "JTI_CLAIM": "jti",
}

ROOT_URLCONF = "server.urls"
ASGI_APPLICATION = "server.routing.application"

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "de-DE"
TIME_ZONE = "Europe/Berlin"
USE_I18N = False
USE_L10N = False
USE_TZ = True

IS_PRODUCTION = parse_boolean(os.getenv("PRODUCTION"))

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
        "CONN_HEALTH_CHECKS": False,
        "TIME_ZONE": TIME_ZONE,
        "CHARSET": "UTF8",
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PROTOCOL = os.getenv("PROTOCOL", "http")
CORS_ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

CSRF_COOKIE_NAME = "csrftoken"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# print("DATABASES", DATABASES)
# print("CORS_ALLOWED_ORIGINS", CORS_ALLOWED_ORIGINS)

# This is only set in IDE (Intellij)
if os.getenv("LOCAL-DEV"):
    # Local-Solution
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
else:
    # Docker-Solution
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [(os.getenv("REDIS_HOST"), 6379)],
            },
        },
    }

REDIS_URL = f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT', 6379)}/1"
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = False
USE_L10N = False
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

DATA_UPLOAD_MAX_NUMBER_FILES = 10000
DATA_UPLOAD_MAX_MEMORY_SIZE = 26843545600  # 5GB
FILE_UPLOAD_MAX_MEMORY_SIZE = 26843545600  # 5GB

DEFAULT_DIRS = {_dir.strip(): os.path.join(MEDIA_ROOT, _dir.strip())
                for _dir in os.getenv("DEFAULT_DIRS", "").split(',')}

DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {"location": DEFAULT_DIRS.get("backup")}
DBBACKUP_CONNECTORS = {
    "default": {
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "CONNECTOR": "dbbackup.db.postgresql.PgDumpConnector"
    }
}

FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
]

# Security

# python manage.py check --deploy

# TODO fix later SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"
SESSION_COOKIE_AGE = 9000
SESSION_COOKIE_SECURE = parse_boolean(os.getenv("SESSION_COOKIE_SECURE", False))

SECURE_REFERRER_POLICY = os.getenv("SECURE_REFERRER_POLICY")
SECURE_HSTS_SECONDS = parse_int(os.getenv("SECURE_HSTS_SECONDS", 0))
SECURE_HSTS_PRELOAD = parse_boolean(os.getenv("SECURE_HSTS_PRELOAD", False))
SECURE_SSL_REDIRECT = parse_boolean(os.getenv("SECURE_SSL_REDIRECT", False))
SECURE_SSL_HOST = os.getenv("SECURE_SSL_HOST")
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# CSRF_COOKIE_SECURE = parse_boolean(os.getenv("CSRF_COOKIE_SECURE", True))
# CSRF_COOKIE_SAMESITE = "Strict"
# CSRF_FAILURE_VIEW = "django.views.csrf.csrf_failure"
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
CSRF_COOKIE_NAME = "csrftoken"
CSRF_USE_SESSIONS = False
