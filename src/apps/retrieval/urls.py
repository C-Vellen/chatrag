from django.urls import re_path
from . import views
from . import apps


app_name = apps.RetrievalConfig.name

urlpatterns = [
    re_path(r"^search/$", views.get_chunks, name="search"),
    
]
