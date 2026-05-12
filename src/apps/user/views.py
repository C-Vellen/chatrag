# from authlib.integrations.django_client import OAuth

from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.core import management
from django.core.exceptions import PermissionDenied

from src.settings import DEBUG
from home.models import Libelles
from .forms import ConnexionForm


def deconnexion(request):
    logout(request)
    return redirect("home:index")


def connexion(request):
    """
    Vue permettant de se connecter
    """

    # suppression des sessions expirées :
    management.call_command("clearsessions")

    context = {lib.description: lib for lib in Libelles.objects.all()}
    context.update(
        {
            "titre_onglet": "connexion",
            "authentication_fail": False,
        }
    )
    if request.method == "POST":
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
            else:
                context.update({"authentication_fail": True})

    form = ConnexionForm()
    context.update({"form": form})

    return render(request, "user/connexion.html", context)


def nonautorise(request):
    raise PermissionDenied
