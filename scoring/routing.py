from django.urls import re_path

from scoring.consumer import DockerConsumer

ws_pattern = [
    # re_path(r'^ws/web-legacy/test/', WebTestConsumer.as_asgi()),
    # re_path(r'^ws/product/test/', UiTestConsumer.as_asgi()),
    # re_path(r'^ws/build/', BuildConsumer.as_asgi()),
    # re_path(r'^ws/stack/', TestStackConsumer.as_asgi()),
    re_path(r'^ws/docker/status', DockerConsumer.as_asgi()),

]
