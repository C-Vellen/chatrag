import uuid
from django.db import models
from django.db.models import Count
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from urllib.parse import urlparse
from src.media_file_cleaning import auto_delete_file_on_delete, auto_delete_file_on_change


SOURCE_TYPE = {
    "TXT":  "Fichier .txt",
    "MD":   "Fichier .md",
    "PDF":  "Fichier .pdf",
    "YT":   "Video youtube",
    "OTH":  "Other"
} 
SOURCE_LOGOS = {
    "TXT":  "TXT.svg",
    "MD":   "MD.svg",
    "PDF":  "PDF.svg",
    "YT":   "youtube.svg",
    "OTH":  "blank.svg",
} 
METRICS = {
    "COSINE": "Distance Cosinus",
    "EUCLIDEAN": "Distance Euclidienne L2",
    "DOT_PRODUCT": "Produit scalaire",
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
    embedding_model = models.CharField(max_length=100, default="BAAI/bge-m3", help_text="relancer l'embedding si modification")
    
    # chunk config
    chunk_size      = models.IntegerField(default=1000, help_text="taille maxi des chunks (en caractères), relancer l'embedding si modification")
    chunk_overlap   = models.IntegerField(default=200, help_text="max chunk overlap (en caractères), relancer l'embedding si modification")
    chunk_number    = models.IntegerField(default=32, help_text="nombre maxi de chunks par batch, à réduire si cpu-only")
    
    # metrics
    metrics          = models.CharField(
        max_length=20, 
        choices=METRICS, 
        default="COSINE",
        help_text="distance entre vecteurs, relancer l'embedding si modification",
        )
  
    class Meta:
        verbose_name = "Collection"

    def __str__(self):
        return f"Collection[{self.collection_name} / {self.embedding_model}]"

    @classmethod
    def get_active(cls) -> "Collection":
        """Retourne la configuration RAG active en cache infini, la config par défaut sinon"""
        config = cache.get("rag_config_active")
        if config is None:
            config = cls.objects.filter(is_active=True).first() or cls()
            cache.set("rag_config_active", config, timeout=None)
        return config

    def save(self, *args, **kwargs):
        """Invalide le cache à chaque sauvegarde via l'admin."""
        cache.delete("rag_config_active")
        super().save(*args, **kwargs)

    
class DocumentRef(models.Model):
    """Référentiel des documents """
    
    class Status(models.TextChoices):
        NEW =           'NEW', _('Nouveaux documents')
        REGISTERED =    'REG', _('Documents ingérés')
        ERROR =         'ERR', _('Documents introuvables')
        IN_PROGRESS =   'WIP', _("En cours d'ingestion")
        
        @classmethod
        def colors(cls):
            return {
                cls.NEW:         "text-gray-500",
                cls.REGISTERED:  "text-gray-800",
                cls.ERROR:       "text-red-600",
                cls.IN_PROGRESS: "text-blue-600",
            }
        
    
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection  = models.ForeignKey("Collection", on_delete=models.CASCADE, related_name="document")
    titre       = models.CharField(max_length=500)
    is_active   = models.BooleanField(default=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE)
    source_origin = models.CharField(max_length=1000)   # uri d'origin entré par l'utilisateur, ou "download"
    source_file = models.FileField(upload_to="ingest/file/", blank=True, null=True)  
    video_id    = models.CharField(max_length=500, blank=True, null=True)
    timestamp   = models.JSONField(default=dict, blank=True, null=True)
    duration    = models.IntegerField(blank=True, null=True) # durée totale d'une video youtube
    
    nb_chunks   = models.IntegerField(blank=True, null=True)
    nb_words    = models.IntegerField(blank=True, null=True)
    nb_chars    = models.IntegerField(blank=True, null=True)
    
    status = models.CharField(
        max_length=3,
        choices=Status.choices,
        default=Status.NEW,
    )
    date  = models.DateTimeField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    
   
    def __str__(self):
        return f"{self.titre[:20]} | {self.source_type} | {self.status}"
    
    @property
    def color(self):
        """Retourne les classes de couleur selon le status """
        # colors = {
        #     self.Status.NEW:        "text-gray-500",
        #     self.Status.REGISTERED: "text-gray-800",
        #     self.Status.ERROR:      "text-red-600",
        #     self.Status.IN_PROGRESS:"text-blue-600",
        # }
        # Retourne une couleur par défaut si le statut est inconnu
        return self.Status.colors().get(self.status, "text-gray-800")
        # return colors.get(self.status, "text-gray-800")
    
    @classmethod
    def docs_stat(cls):
        """Retourne le nombre de documents par status """
        counts = cls.objects.values_list('status').annotate(total=Count('id'))
        counts_dict = dict(counts)
        
        color_map = cls.Status.colors()

        return [
            {
                'status':   status.value,
                'label':    status.label,
                'count':    counts_dict.get(status.value, 0),
                'color':    color_map.get(status.value, "text-gray-800")
            }
            for status in cls.Status
        ]    
        
    
    @property
    def datef(self):
        """Retourne la date sous forme de chaîne au format jj/mm/aaaa."""
        if self.date:
            return self.date.strftime("%d/%m/%Y")
        return ""
    
    
    def get_file(self):
        """ liste des fichiers media, pour gérer leur mise à jour et suppression """
        return [self.source_file]
    

    @property
    def source_logo(self):
        # On définit le dictionnaire de correspondance "source -> nom de l'image"
               
        # On récupère le bon logo. Si la source est inconnue, on fournit un logo par défaut.
        nom_logo = SOURCE_LOGOS.get(self.source_type, "OTH")
        
        # On retourne le chemin complet vers le dossier static
        return f"img/{nom_logo}"
    
    @property
    def source_url(self):
        if self.source_type == "YT":
            return self.source_origin
        elif self.source_file:
            return self.source_file.url
        return "#"
    

class WaitingList(models.Model):
    """ Documents alimentés par API pour sélection groupée et ingestion """
    
    class Status(models.TextChoices):
        NEW =           'NEW', _('Nouveau document')
        REGISTERED =    'REG', _('Document ingéré')
        ERROR =         'ERR', _('Introuvable')
        
        
    titre       = models.CharField(max_length=500)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE, default="OTH")
    source_origin = models.CharField(max_length=1000, blank=True, null=True)   # uri d'origin entré par l'utilisateur, ou "download"
    video_id    = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(
        max_length=3,
        choices=Status.choices,
        default=Status.NEW,
    )
    date  = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.titre} [{self.id}]"
    
    @property
    def color(self):
        """Retourne les classes de couleur selon le status """
        colors = {
            self.Status.NEW: "bg-blue-100",
            self.Status.REGISTERED: "bg-green-100",
            self.Status.ERROR: "bg-red-100",
        }
        # Retourne une couleur par défaut si le statut est inconnu
        return colors.get(self.status, "bg-gray-100 text-gray-800")
    
    @property
    def datef(self):
        """Retourne la date sous forme de chaîne au format jj/mm/aaaa."""
        if self.date:
            return self.date.strftime("%d/%m/%Y")
        return ""
    

# Suppression des fichiers MEDIAROOT inutiles lors de la mise à jour ou suppression
@receiver(post_delete, sender=DocumentRef)
def auto_delete_document_on_delete(sender, instance, **kwargs):
    auto_delete_file_on_delete(sender, instance) 

@receiver(pre_save, sender=DocumentRef)
def auto_delete_document_on_change(sender, instance, **kwargs):
    auto_delete_file_on_change(sender, instance) 

# Libère le cache pour forcer la mise à jour de la configuration rag (collection)
@receiver([post_save, post_delete], sender=Collection)
def clear_config_cache(sender, instance, **kwargs):
    cache.delete("rag_config_active") 

