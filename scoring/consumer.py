import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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


