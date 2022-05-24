import json
import threading

import docker
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from scoring.helper import sleep_ms, ilog

GRP_NAME = "command-group"


class CommandConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = GRP_NAME
        self.kwargs = {}

    async def connect(self):
        self.kwargs = self.scope['url_route']['kwargs']

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, **kwargs):
        kwargs.update({'type': 'command_result'})

        print("forward", kwargs)
        await self.channel_layer.group_send(
            self.group_name, kwargs
        )

    # Receive message from test group
    async def command_result(self, event):
        print("command_result event", event)
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))


# ######################################################################################################################


class DockerConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = "docker"
        self.route = {}
        self.listener = None

    async def connect(self):
        self.route = self.scope["url_route"]["kwargs"]
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        self.change_listener_connect(True)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        self.change_listener_connect(False)

    async def receive(self, text_data, **kwargs):
        ilog(f"RECEIVE WS: {text_data} | kwargs: {kwargs}")

        js = json.loads(text_data)
        js["type"] = "docker_status"

        await self.channel_layer.group_send(
            self.group_name, js
        )

    async def docker_status(self, event):
        await self.send(text_data=json.dumps(event))

    def change_listener_connect(self, starting):
        ilog("Starting Docker-Listener", starting)
        if starting:
            self.listener = threading.Thread(target=docker_status_listener, args=(get_docker_status(),))
            self.listener.start()
        else:
            self.listener.running = False

def docker_status_listener(_data):
    data = {}
    for container in _data:
        data.update({container.get("id"): {"name": container.get("name"), "status": container.get("status")}})

    current = threading.currentThread()
    while getattr(current, "running", True):
        sleep_ms(5000)
        updated = {}
        removed = []
        valid_check = set()
        containers = get_docker_status()

        for container in containers:
            _id = container.get("id")
            name = container.get("name")
            status = container.get("status")
            valid_check.add(_id)

            # New OR Updated
            if _id not in data or data.get(_id).get("status") != status:
                obj = {_id: {"name": name, "status": status}}
                data.update(obj)
                updated.update(obj)

        # Removed
        for key in data:
            if key not in valid_check:
                removed.append(key)

        for key in removed:
            data.pop(key)

        if len(updated):
            broadcast_docker_status("updated", updated)

        if len(removed):
            broadcast_docker_status("removed", removed)


def get_docker_status() -> list:
    client = docker.from_env()
    cons = []
    for container in client.containers.list(all=True):
        cons.append({"id": container.id,
                     "name": container.name,
                     "status": container.status})
    return cons


def broadcast_docker_status(event, data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "docker",
        {
            "type": "docker_status",
            "event": event,
            "data": data,
        }
    )
