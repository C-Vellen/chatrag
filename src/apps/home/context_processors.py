from .models import Libelles, Style
from src.settings import DEBUG


def inject_style(request):
    # Récupère le style actif
    style = Style.get_active()
    return {'style': style}

def inject_context(request):
    # Récupère le style actif
    context = {lib.description:lib for lib in Libelles.objects.all()}
    context.update({
        "debug": DEBUG,
        "user": request.user,
            })
    return context