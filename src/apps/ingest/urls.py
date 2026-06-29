from django.urls import path, re_path
from . import views
from . import apps


app_name = apps.IngestConfig.name

urlpatterns = [
    re_path(r"^list/$", views.documents_list, name="documents_list"),
    path("read_chunks/<uuid:document_id>/", views.read_chunks, name="read_chunks"),
    path("remove_document/<uuid:document_id>/", views.remove_document, name="remove_document"),
    path("update_list/", views.update_list, name="update_list"),
]
