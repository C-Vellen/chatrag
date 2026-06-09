from django.urls import path
from . import views
from . import apps


app_name = apps.ChatConfig.name

urlpatterns = [
    path("",        views.chat_view,   name="chat"),
    path("stream/", views.stream_view, name="chat-stream"),
]
