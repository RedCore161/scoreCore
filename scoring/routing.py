from django.urls import re_path

from scoring.consumer import DockerConsumer

ws_pattern = [
    re_path(r'^ws/docker/status', DockerConsumer.as_asgi()),
]
