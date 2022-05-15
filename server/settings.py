import os

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / "subdir".
from server.read_env import read_env

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

ENV_FILE_PATH = os.path.join(BASE_DIR, "django.env")

read_env(ENV_FILE_PATH)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")
# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = os.getenv("DEBUG") == "1"

ADB_BASE = os.getenv("ADB_BASE")

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
    "rest_auth",
    "dbbackup",

    "corsheaders",

    "channels",
    "django_q",

    "scoring",
]

outtime = 60 * 60 * 4

Q_CLUSTER = {
    "name": "DjangORM",
    "workers": 4,

    "queue_limit": 15,
    "bulk": 10,
    "recycle": 500,
    "save_limit": 10,
    "cpu_affinity": 1,
    "ack_failures": True,
    "max_attempts": 1,
    "timeout": outtime,
    "retry": outtime + 300,
    "orm": "default",
    "has_replica": True,
    # "redis": {
    #     "host": os.getenv("REDIS_HOST"),
    #     "port": 6379,
    #     "db": 0,
    #     "charset": "utf-8",
    #     "errors": "strict",
    # },
    # "error_reporter": {
    #     "rollbar": {
    #         "access_token": "GET-A-KEY",
    #         "environment": "Django-Q"
    #     }
    # }
}

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': 'uitests-control-cache:11211',
#     }
# }

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

REST_FRAMEWORK = {
    "DATETIME_FORMAT": "%d.%m.%Y, %H:%M:%S",

    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ]
}

REST_AUTH_SERIALIZERS = {
    'TOKEN_SERIALIZER': 'scoring.serializers.TokenSerializer',
}

ROOT_URLCONF = "server.urls"

ASGI_APPLICATION = "server.routing.application"

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

PROTOCOL = os.getenv('PROTOCOL', 'http')
HARD_IP = os.getenv('HARD_IP', 'ignore.local')

CORS_ALLOWED_ORIGINS = [
    f"{PROTOCOL}://{HARD_IP}",
    f"{PROTOCOL}://localhost:3000",
    f"{PROTOCOL}://localhost:8000",
    f"{PROTOCOL}://scoring.local",
    f"{PROTOCOL}://api.scoring.local",
    f"{PROTOCOL}://scoring-backend:8000",
]
CSRF_COOKIE_NAME = "csrftoken"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


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

BACKUP_DIR = os.path.join(MEDIA_ROOT, os.getenv("BACKUP_DIR", "backup"))
SETUP_DIR = os.path.join(MEDIA_ROOT, os.getenv("SETUP_DIR", "setup"))
UPLOAD_DIR = os.path.join(MEDIA_ROOT, os.getenv("UPLOAD_DIR", "upload"))
EXPORT_DIR = os.path.join(MEDIA_ROOT, os.getenv("EXPORT_DIR", "export"))

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': BACKUP_DIR}
DBBACKUP_HOSTNAME = HARD_IP

SCREENSHOT_FILENAME = "current.png"

PRINT_EMULATOR_COMMANDS = True


# Security

# python manage.py check --deploy

# CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_SAMESITE = "Strict"
# SESSION_COOKIE_SECURE = True

# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_SSL_REDIRECT = True
# X_FRAME_OPTIONS = "DENY"
# SECURE_HSTS_SECONDS = 300  # set low, but when site is ready for deployment, set to at least 15768000 (6 months)
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

