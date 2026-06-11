from django.shortcuts import render


def index(request):
    context = {
            "titre_onglet": "Titre-onglet",
        }
    return render(request, "home/index.html", context)
