import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.local")

from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .jwt_auth_middleware import JWTAuthMiddleware
import chat.routing

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(
            AuthMiddlewareStack(
                URLRouter(
                    chat.routing.websocket_urlpatterns
                )
            )
        ),
    }
)