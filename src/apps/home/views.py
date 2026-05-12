from django.shortcuts import render
from .context import usercontext


def index(request):
    context = usercontext(request)
    context.update(
        {
            "titre_onglet": "Titre-onglet",
        }
    )
    return render(request, "home/index.html", context)
