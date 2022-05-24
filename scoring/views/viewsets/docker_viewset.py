import docker
from django_q.tasks import async_task
from docker.errors import NotFound
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from scoring.consumer import get_docker_status
from scoring.tasks import task_stop_docker_container
from server.views import RequestSuccess, RequestFailed


class DockerViewSet(viewsets.ViewSet):

    authentication_classes = (TokenAuthentication, )

    @action(detail=False, url_path="status", methods=["GET"])
    def docker_status(self, request: Request):
        return Response({"container": get_docker_status()})

    @action(detail=False, url_path="restart", methods=["POST"])
    def restart_docker_container(self, request: Request):
        container_id = request.data.get("container_id")

        if container_id:
            client = docker.from_env()
            container = client.containers.get(container_id)
            if container:
                container.restart()
                return RequestSuccess()

        return RequestFailed()

    @action(detail=False, url_path="remove", methods=["POST"])
    def remove_docker_container(self, request: Request):

        container_id = request.data.get("container_id")

        if container_id:
            client = docker.from_env()
            container = client.containers.get(container_id)
            if container:
                container.remove()
                return RequestSuccess()

        return RequestFailed()

    @action(detail=False, url_path="stop", methods=["POST"])
    def stop_docker_container(self, request: Request):

        container_id = request.data.get("container_id")
        if container_id:
            async_task(task_stop_docker_container, container_id, task_name="stopping-docker-container")
            return RequestSuccess()

        container = request.data.get("container")
        if container:
            async_task(task_stop_docker_container, container_id, task_name="stopping-docker-container")
            return RequestSuccess()

        return RequestFailed()

    @action(detail=False, url_path="logs", methods=["POST"])
    def get_container_logs(self, request: Request):

        container_id = request.data.get("container_id")

        if container_id:
            client = docker.from_env()
            container = client.containers.get(container_id)
            if container:
                return RequestSuccess({"logs": container.logs(), "name": f"Logs of '{container.name}'"})

        return RequestFailed()

    @action(detail=False, url_path="ping", methods=["GET", "POST"])
    def ping_docker(self, request: Request):
        name = request.data.get("name")
        if name:
            client = docker.from_env()
            try:
                container = client.containers.get(name)
                if container:
                    return Response({"running": container.attrs["State"].get("Status") == "running"})
            except NotFound:
                pass

        return Response({"running": False})
