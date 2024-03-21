# Yenda/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<sender_id>\d+)/$", consumers.ChatConsumer.as_asgi())
]