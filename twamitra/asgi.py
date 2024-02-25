"""
ASGI config for myproject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'twamitra.settings')

django.setup()


django_asgi_app = get_asgi_application()

import chatApp.routing


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": 
            AuthMiddlewareStack(URLRouter(chatApp.routing.websocket_urlpatterns))
        ,
    }
)