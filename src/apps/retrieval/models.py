from django.db import models
from solo.models import SingletonModel

# Create your models here.

SEARCH_TYPES = {
    "similarity": "similarity: retourne les k chunks les plus proches",
    "similarity_score_threshold": "similarity_score_threshold: retourne les k chunks les plus proches filtrés par score minimum",
    "mmr": "mmr: maximum marginal relevance" 
}


class RetrivConfig(SingletonModel):
    
    k = models.IntegerField(default=4, help_text="nombre de chunks retournés")
    search_type = models.CharField(max_length=50, choices=SEARCH_TYPES, default="similarity")
    
    # hyperparamètres spécifiques pour similarity_score_threshold:
    score_threshold = models.FloatField(default=0.4, help_text="avec similarity_score_threshold | score_minimum pour sélectionner un chunk")
    
    # hyperparamètres spécifiques pour mmr:
    fetch_k = models.IntegerField(default=20, help_text="avec mmr | chunks candidats analysés avant sélection")
    lambda_mult = models.FloatField(default=0.5, help_text="avec mmr | 0=max diversité, 1=max similarité")
    
    def __str__(self):
        return "Configuration Retriever"
    
    
    
    