from django.urls import path
from .consumers import OrderConsumer

websocket_urlpatterns = [
    path("ws/orders/<int:seller_id>/", OrderConsumer.as_asgi()),
]
