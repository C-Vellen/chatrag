from django.urls import path, re_path
from . import views
from . import apps


app_name = apps.IngestConfig.name

urlpatterns = [
    re_path(r"^list/$", views.documents_list, name="documents_list"),
    path("view_document/<uuid:document_id>/", views.view_document, name="view_document"),
    path("remove_document/<uuid:document_id>/", views.remove_document, name="remove_document"),
]
