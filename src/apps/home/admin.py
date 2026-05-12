from django.contrib import admin
from .models import Libelles, DefaultContent

@admin.register(Libelles)
class LibellesAdmin(admin.ModelAdmin):
    
    # affichage des libellés 
    list_display = [
        'description',
        'explication',
        'contenu',
        'image',
        'fichier', 
        'lien',
    ]

@admin.register(DefaultContent)
class DefaultContentAdmin(admin.ModelAdmin):
    
    # affichage des contenus par défaut
    list_display = [
        'description',
        'explication',
        'contenu',
        'image',
        'fichier', 
    ]
      