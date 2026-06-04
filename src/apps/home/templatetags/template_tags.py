from django import template
from django.http import Http404
from django.utils import lorem_ipsum
from src.settings import MEDIA_URL
from home.models import default_image_url

register = template.Library()


# récupération des images :
@register.filter
def find_img(content):
    """recherche de l'image associée au contenu dans la BD, et de l'image par défaut si pas d'image """
    try:
        return content.image.url
    except (AttributeError, ValueError) :
        return MEDIA_URL + default_image_url()  

# récupération des fichiers :
@register.filter
def find_file(content):
    """recherche du fichier associée au contenu dans la BD, et de l'image par défaut si pas d'image """
    try:
        return content.fichier.url
    except (AttributeError, ValueError) :
        return ""  
    
@register.filter
def find_content(content, n):
    """recherche du contenu, sinon par défaut morem_ipsum de n mots """
    try:
        return content.contenu
    except (AttributeError, ValueError) :
        # return lorem_ipsum.COMMON_P
        return lorem_ipsum.words(n,True)
    
@register.filter
def initiales(user):
    """renvoie les initiales de user"""
    if user.is_anonymous:
        return "👤"
    else:
        try:
            first = user.first_name[0].upper()
        except IndexError:
            first = ""
        try:
            last = user.last_name[0].upper()
        except IndexError:
            last = ""
        return first + last

@register.filter
def find_name(user):
    """renvoie les prénoms et nom de user"""
    if user.is_anonymous:
        return ""
    else:
        first = user.first_name
        last = user.last_name
 
        return f"{first} {last}"
    

@register.filter
def format_time(seconds):
    """Transforme des secondes (ex: 75.5) en chaîne lisible (ex: '01:15')"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


