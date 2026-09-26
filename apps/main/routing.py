from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path(
        "ws/updates/<int:application_id>/",
        consumers.RealtimeConsumer.as_asgi(),
    ),
    path("ws/updates/", consumers.RealtimeConsumer.as_asgi()),
]
