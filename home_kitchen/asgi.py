import os
from django.core.asgi import get_asgi_application
from home_kitchen.socket_server import app as socket_app

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "home_kitchen.settings")

django_app = get_asgi_application()

application = socket_app
