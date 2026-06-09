from django.contrib import admin
from .models import LLMModel, Conversation, Message


@admin.register(Conversation)
class LLMModelAdmin(admin.ModelAdmin):

    # affichage des libellés
    list_display = ["id", "created_at", "updated_at", "title"]

@admin.register(Message)
class LLMModelAdmin(admin.ModelAdmin):

    # affichage des libellés
    list_display = ["id", "conversation", "role", "content", "created_at"]

@admin.register(LLMModel)
class LLMModelAdmin(admin.ModelAdmin):

    # affichage des libellés
    list_display = ["id", "LLM", "temperature", "verbosity", "active"]

