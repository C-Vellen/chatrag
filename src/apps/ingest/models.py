from django.db import models
from django.core.cache import cache



class EmbeddingConfig(models.Model):
    """ 
    embedding parameters 
    warning: any change in these parameters need to re-run embedding of all documents
    or to run embeddings with a new collection_name
    """
    collection_name = models.CharField(max_length=100, default="documents", help_text="exemple: documents_chunk1000_bge-m3")
    is_active = models.BooleanField(default=True)
    embedding_model = models.CharField(max_length=100, default="BAAI/bge-m3", help_text="relancer l'embedding si modificaiton")
    
    # chunk config
    chunk_size = models.IntegerField(default=1000, help_text="taille maxi des cunks (en caractères), relancer l'embedding si modificaiton")
    chunk_overlap = models.IntegerField(default=200, help_text="max chunk overlap (en caractères), relancer l'embedding si modificaiton")
    chunk_number = models.IntegerField(default=32, help_text="nombre maxi de chunks par batch, à réduire si cpu-only")
    
  
    class Meta:
        verbose_name = "Embedding Configuration"

    def __str__(self):
        return f"EmbeddingConfig [{self.collection_name} / {self.embedding_model}]"

    @classmethod
    def get_active(cls) -> "EmbeddingConfig":
        """Returns active config with 5 minutes cache."""
        config = cache.get("rag_config_active")
        if config is None:
            config = cls.objects.filter(is_active=True).first()
            cache.set("rag_config_active", config, timeout=300)
        return config

    def save(self, *args, **kwargs):
        """Invalide le cache à chaque sauvegarde via l'admin."""
        cache.delete("rag_config_active")
        super().save(*args, **kwargs)

    
