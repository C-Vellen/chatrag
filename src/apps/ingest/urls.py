from django.urls import re_path
from . import views
from . import apps


app_name = apps.IngestConfig.name

urlpatterns = [
    re_path(r"^list/$", views.documents_list, name="documents_list"),
    re_path(r"^view_documents/(?P<source>.+)/$", views.view_document, name="view_document"),
    re_path(r"^remove_document/(?P<source>.+)/$", views.remove_document, name="remove_document"),

]
