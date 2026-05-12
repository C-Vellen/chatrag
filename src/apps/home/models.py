from django.db import models
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models.signals import post_delete, pre_save
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
    contenu = models.TextField(blank=True)
    image = models.ImageField(upload_to="home/images/", null=True, blank=True)
    fichier = models.FileField(upload_to="home/files/", null=True, blank=True) 

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
    contenu qui sera transmis au template pour affichage de la page 
    """
    description = models.CharField(max_length=50, default='')
    explication = models.TextField(blank=True)
    contenu = models.TextField(blank=True)
    image = models.ImageField(upload_to="home/images/", null=True, blank=True)
    fichier = models.FileField(upload_to="home/files/", null=True, blank=True) 
    lien = models.URLField(blank=True) 

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


# Suppression des fichiers MEDIAROOT inutiles lors de la mise à jour ou suppression
@receiver(post_delete, sender=Libelles)
def auto_delete_miniatures_on_delete(sender, instance, **kwargs):
    auto_delete_file_on_delete(sender, instance) 

@receiver(pre_save, sender=Libelles)
def auto_delete_miniatures_on_change(sender, instance, **kwargs):
    auto_delete_file_on_change(sender, instance) 



