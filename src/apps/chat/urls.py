from django.urls import re_path
from . import views
from . import apps


app_name = apps.ChatConfig.name

urlpatterns = [
    re_path(r"^talk/$", views.talk, name="talk"),
    
]