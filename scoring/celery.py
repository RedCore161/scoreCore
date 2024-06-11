import os

import docker
from celery import Celery
from celery.signals import setup_logging, task_postrun, task_prerun
from celery.utils.log import get_task_logger
from django.utils import timezone
from kombu.serialization import registry

from scoring.helper import dlog
from server import settings

# ######################################################################################################################

logger = get_task_logger(__name__)

_redis = f'redis://{os.getenv("REDIS_HOST", "localhost")}:{os.getenv("REDIS_PORT", 6379)}/1'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

celery_instance = Celery("server")
registry.enable("json")

celery_instance.conf.update(
    task_serializer="json",
    result_serializer="json",
    timezone="Europe/Berlin",
    enable_utc=True,
    task_store_errors_even_if_ignored=True,
    task_soft_time_limit=3600,                  # 60*60s = 1h
    task_acks_on_failure_or_timeout=True,
    result_extended=True,
    result_backend="django-db",
    cache_backend="django-cache",
    broker_url=_redis,
)
celery_instance.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# List to store running tasks
running_tasks = {}


# ######################################################################################################################


@setup_logging.connect
def configure_logging(*args, **kwargs):
    from logging.config import dictConfig

    from django.conf import settings
    dictConfig(settings.LOGGING)


@task_prerun.connect
def task_started_handler(task_id, task, *args, **kwargs):
    dlog(f"PreRun {args=} | {kwargs=}", logger=logger)
    running_tasks[task_id] = {"name": task.name, "status": "running"}


@task_postrun.connect
def task_completed_handler(task_id, task, *args, **kwargs):
    from django_celery_results.models import TaskResult

    dlog(f"PostRun | {task_id=} | {args=}",  logger=logger)
    result = TaskResult.objects.get(task_id=task_id)
    dlog("TaskResult", f"result={result.result}")
    if task_id in running_tasks:
        running_tasks[task_id].update({"status": "done", "time": timezone.now().strftime("%Y-%m-%d %H:%M:%S")})


@celery_instance.task
def task_stop_docker_container(container: str, *args, **kwargs):
    """
    stops a docker container
    :param container: container-id
    """
    client = docker.from_env()
    cont = client.containers.get(container)
    if cont:
        cont.stop()
    return {"success": True}


@celery_instance.task
def list_running_tasks():
    return running_tasks


@celery_instance.task
def debugging(cmd, *args, **kwargs):
    return {"cmd": cmd, **kwargs}

