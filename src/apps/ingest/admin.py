from django.contrib import admin
from .models import EmbeddingConfig

@admin.register(EmbeddingConfig)
class EmbeddingConfigAdmin(admin.ModelAdmin):
    list_display = ["collection_name", "embedding_model", "chunk_size", "chunk_overlap", "chunk_number", "is_active"]