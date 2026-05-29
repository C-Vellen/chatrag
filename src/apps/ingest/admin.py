from django.contrib import admin
from .models import Collection, DocumentRef

    
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["id", "collection_id", "collection_name", "embedding_model", "chunk_size", "chunk_overlap", "chunk_number", "is_active"]
    
    readonly_fields = ("id", "collection_id",)
    
    
@admin.register(DocumentRef)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["id", "collection", "titre", "is_active", "created_at", "source_type", "source_origin", "source_file", "nb_chunks", "nb_words", "nb_chars"]
    
    readonly_fields = ("id","collection", "nb_chunks", "nb_words", "nb_chars")