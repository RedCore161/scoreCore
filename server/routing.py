from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from scoring.routing import ws_pattern

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(ws_pattern)
        )
    )
})
