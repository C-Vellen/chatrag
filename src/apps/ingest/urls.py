from django.urls import path, re_path
from . import views
from . import apps


app_name = apps.IngestConfig.name

urlpatterns = [
    re_path(r"^list/$", views.documents_list, name="documents_list"),
    path("read_chunks/<uuid:document_id>/", views.read_chunks, name="read_chunks"),
    path("remove_document/<uuid:document_id>/", views.remove_document, name="remove_document"),
    path("waiting_list/", views.waiting_list, name="waiting_list"),
    path("updatewaitinglist/", views.update_waiting_list, name="update_waiting_list"),
]
