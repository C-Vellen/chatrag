import uuid
from django.db import models
from django.core.cache import cache
from django.core.exceptions import ValidationError
from urllib.parse import urlparse


DOCUMENT_SOURCE_TYPE = {
    "TXF":  "Fichier .txt",
    "PDF":  "Fichier .pdf",
    "MDF":  "Fichier .md",
    "TXP":  "Chemin vers fichier .txt",
    "PDP":  "Chemin vers fichier .pdf",
    "MDP":  "Chemin vers fichier .md",
    "YTU":  "URL Video Youtube",
    "OTH":  "other format"
} 


def valider_uri(valeur):
    """ Validation d'une URI (chemin vers un fichier ou url) """
    try:
        resultat = urlparse(valeur)
        # Une URI valide doit au moins avoir un schéma (ex: urn, file, http) 
        # ou un chemin (path)
        if not resultat.scheme and not resultat.path:
            raise ValidationError("Ceci n'est pas une URI valide.")
    except Exception:
        raise ValidationError("Format d'URI invalide.")


class Collection(models.Model):
    """ 
    collection parameters
    warning: any change in these parameters need to re-run embedding of all documents
    or to run embeddings with a new collection_name
    """
    collection_name = models.CharField(max_length=100, default="documents", help_text="exemple: documents_chunk1000_bge-m3")
    collection_id   = models.CharField(max_length=50, blank=False)
    is_active       = models.BooleanField(default=True)
    embedding_model = models.CharField(max_length=100, default="BAAI/bge-m3", help_text="relancer l'embedding si modificaiton")
    
    # chunk config
    chunk_size      = models.IntegerField(default=1000, help_text="taille maxi des cunks (en caractères), relancer l'embedding si modificaiton")
    chunk_overlap   = models.IntegerField(default=200, help_text="max chunk overlap (en caractères), relancer l'embedding si modificaiton")
    chunk_number    = models.IntegerField(default=32, help_text="nombre maxi de chunks par batch, à réduire si cpu-only")
    
  
    class Meta:
        verbose_name = "Collection"

    def __str__(self):
        return f"Collection[{self.collection_name} / {self.embedding_model}]"

    @classmethod
    def get_active(cls) -> "Collection":
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

    
class DocumentRef(models.Model):
    """Référentiel des documents ingérés dans pgvector."""
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection  = models.ForeignKey("Collection", on_delete=models.CASCADE, related_name="document")
    titre       = models.CharField(max_length=500)
    is_active   = models.BooleanField(default=True)
    type_source = models.CharField(max_length=20, choices=DOCUMENT_SOURCE_TYPE)
    source_uri  = models.CharField(max_length=1000, validators=[valider_uri], blank=True, null=True) # uri = URL ou path
    source_file = models.FileField(upload_to="ingest/file/", blank=True, null=True)  
    nb_chunks   = models.IntegerField(blank=True, null=True)
    nb_words    = models.IntegerField(blank=True, null=True)
    nb_chars    = models.IntegerField(blank=True, null=True)
     
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titre} ({self.id})"