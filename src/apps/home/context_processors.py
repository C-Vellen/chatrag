from .models import Styles


def inject_style(request):
    # Récupère le style actif
    style = Styles.get_active()
    return {'style': style}