from django.db import models
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models.signals import post_delete, pre_save, post_save
from django.core.cache import cache
from src.settings import MEDIA_URL
from src.media_file_cleaning import auto_delete_file_on_delete, auto_delete_file_on_change
from . import apps




def default_image_url():
    """
    retourne l'url de l'image par défaut
    """
    try:
        default_content = get_object_or_404(DefaultContent, description="default_image")
        return default_content.image.url.replace(MEDIA_URL, '/')
    except (Http404, ValueError):
        return "static/img/img_default.svg"


class DefaultContent(models.Model):
    """
    contenu par défaut (notamment pour les images) 
    """
    description = models.CharField(max_length=50, default='')
    explication = models.TextField(blank=True)
    contenu     = models.TextField(blank=True)
    image       = models.ImageField(upload_to="home/images/", null=True, blank=True)
    fichier     = models.FileField(upload_to="home/files/", null=True, blank=True) 

    class Meta:
        app_label = apps.HomeConfig.label
        verbose_name = "Contenu par défaut"

    def __str__(self):
        return self.description

    def get_file(self):
        """ liste des fichiers media, pour gérer leur mise à jour et suppression """
        return [self.image, self.fichier ]
    
    @classmethod
    def create(cls, **kwargs):
        newinstance = "déjà existant"
        try:
            cls.objects.get(description=kwargs["description"])
        except cls.DoesNotExist:
            newinstance = "vient d'être créé"
            instance = cls(**kwargs)
            instance.save()
        print('   DefaultContent {} : ok - {}'.format( kwargs["description"], newinstance))
   

class Libelles(models.Model):
    """
    contenu qui sera transmis aux templates via le context-processor :
    titres, textes, logos, liens url, ...
    """
    description = models.CharField(max_length=50, default='')
    explication = models.TextField(blank=True)
    contenu     = models.TextField(blank=True)
    image       = models.ImageField(upload_to="home/images/", null=True, blank=True)
    fichier     = models.FileField(upload_to="home/files/", null=True, blank=True) 
    lien        = models.URLField(blank=True) 

    class Meta:
        verbose_name = "libellé"

    def __str__(self):
        return self.description

    def get_file(self):
        """ liste des fichiers media, pour gérer leur mise à jour et suppression """
        return [self.image, self.fichier ]

    @classmethod
    def create(cls, **kwargs):
        newinstance = "déjà existant"
        try:
            cls.objects.get(description=kwargs["description"])
        except cls.DoesNotExist:
            newinstance = "vient d'être créé"
            instance = cls(**kwargs)
            instance.save()
        print('   Libelles {} : ok - {}'.format( kwargs["description"], newinstance))           


class Style(models.Model):
    """
    Style qui sera appliqué aux templates via le context-processor
    """
    name            = models.CharField(max_length=50, default="Style par défaut")
    color_bg        = models.CharField(max_length=7, default="#FFFFFF", help_text="couleur de fond")
    color_header    = models.CharField(max_length=7, default="#222999", help_text="couleur du bandeau en-tête")
    lightcolor_text = models.CharField(max_length=7, default="#FFFFFF", help_text="couleur de police / fond clair")
    darkcolor_text  = models.CharField(max_length=7, default="#000000", help_text="couleur de police / fond foncé")
    color_btn       = models.CharField(max_length=7, default="#222999", help_text="couleur des boutons")
    hovercolor_btn  = models.CharField(max_length=7, default="#3F49D6", help_text="couleur des boutons en hover")
    focuscolor_line = models.CharField(max_length=7, default="#FEF08A", help_text="surlignage de texte")
    hovercolor_line = models.CharField(max_length=7, default="#FACC15", help_text="surlignage en hover")
    active          = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_active(cls) -> "Style":
        """Retourne le style actif en cache infini, un style par défaut sinon"""
        style = cache.get("style_active")
        if style is None:
            style = cls.objects.filter(active=True).first() or cls()
            cache.set("style_active", style, timeout=None)
        return style


# Suppression des fichiers MEDIAROOT inutiles lors de la mise à jour ou suppression
@receiver(post_delete, sender=Libelles)
def auto_delete_content_on_delete(sender, instance, **kwargs):
    auto_delete_file_on_delete(sender, instance) 

@receiver(pre_save, sender=Libelles)
def auto_delete_content_on_change(sender, instance, **kwargs):
    auto_delete_file_on_change(sender, instance) 

# Libère le cache pour forcer la mise à jour des styles
@receiver([post_save, post_delete], sender=Style)
def clear_style_cache(sender, instance, **kwargs):
    cache.delete("style_active") 


