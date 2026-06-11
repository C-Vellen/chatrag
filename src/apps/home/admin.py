from django.contrib import admin
from .models import Libelles, DefaultContent, Style

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
      
      
@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    
    # affichage des contenus par défaut
    list_display = [
        'name',
        'color_bg',
        'color_header',
        'lightcolor_text',
        'darkcolor_text',
        'color_btn',
        'hovercolor_btn',
        'focuscolor_line',
        'hovercolor_line',
        'active',
    ]
      