from django.contrib import admin
from .models import EmbeddingConfig, Collection, Document

@admin.register(EmbeddingConfig)
class EmbeddingConfigAdmin(admin.ModelAdmin):
    list_display = ["collection_name", "embedding_model", "chunk_size", "chunk_overlap", "chunk_number", "is_active"]
    
    
    
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["collection_name", "embedding_model", "chunk_size", "chunk_overlap", "chunk_number", "is_active"]
    
    readonly_fields = ("collection_id",)
    
    
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["id", "collection", "titre", "is_active", "created_at", "type_source", "source_text", "source_file", "nb_chunks", "nb_words", "nb_chars"]
    
    readonly_fields = ("id","collection", "nb_chunks", "nb_words", "nb_chars")