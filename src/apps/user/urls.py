from django.urls import path, re_path
from . import views


app_name = "user"

urlpatterns = [
    path("deconnexion/", views.deconnexion, name="deconnexion"),
    path("connexion/", views.connexion, name="connexion"),
    re_path(r"^nonautorise$", views.nonautorise, name="nonautorise"),
]
