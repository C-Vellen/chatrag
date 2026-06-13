from django.urls import path
from . import views
from . import apps


app_name = apps.ChatConfig.name

urlpatterns = [
    path("",        views.chat_view,   name="chat"),
    path("stream/", views.stream_view, name="chat-stream"),
    path("chunks/<uuid:conversation_id>/", views.get_chunks_view, name="chat-chunks"),
    path("chunks/", views.get_chunks_view, name="chat-chunks-base"),
]

