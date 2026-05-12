from home.models import Libelles
from src.settings import DEBUG


def usercontext(request):
    context = {lib.description:lib for lib in Libelles.objects.all()}
    context.update({
        "debug": DEBUG,
        "user": request.user,
            })
    return context