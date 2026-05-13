from django.urls import re_path
from . import views
from . import apps


app_name = apps.IngestConfig.name

urlpatterns = [
    re_path(r"^list/$", views.documents_list, name="list"),
    
]
