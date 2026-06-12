import uuid
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from django.core.cache import cache
from django.db import models


class SystemPrompt(models.Model):
    SYSTEM_PROMPT = "Tu es un assistant expert. Réponds à la question en te basant uniquement sur le contexte fourni. Si la réponse ne s'y trouve pas, dis-le clairement.Réponds en français."
    
    prompt  = models.TextField(default=SYSTEM_PROMPT)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"system_prompt | {self.id}"
    
    @classmethod
    def get_active(cls) -> "SystemPrompt":
        """Retourne le system prompt actif en cache infini, un prompt par défaut sinon"""
        system_prompt = cache.get("systemprompt_active")
        if system_prompt is None:
            system_prompt = cls.objects.filter(active=True).first() or cls()
            cache.set("systemprompt_active", system_prompt, timeout=None)
        return system_prompt  
   
   
class Conversation(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title      = models.CharField(max_length=255, blank=True, default="")
    user       = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="conversation")

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation {self.id} — {self.created_at:%d/%m/%Y %H:%M}"


class Message(models.Model):
    ROLES = {"user": "Utilisateur", "assistant": "Assistant"}

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation    = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role            = models.CharField(max_length=20, choices=ROLES)
    content         = models.TextField()
    created_at      = models.DateTimeField(auto_now_add=True)

    # Métadonnées RAG — chunks utilisés pour cette réponse
    chunks_used     = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["created_at"]
        

class LLMModel(models.Model):
    """
    LLM Model features
    """
    VERBOSITY_LIST = (("Low", "Low"), ("Medium", "Medium"), ("High", "High"))

    LLM = models.CharField(max_length=200, default="")
    temperature = models.FloatField()
    verbosity = models.CharField(max_length=20, choices=VERBOSITY_LIST)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Modèle de LLM"

    @classmethod
    def get_active_model(cls):
        llm_model, created = cls.objects.get_or_create(
            active=True,
            defaults={"LLM": "gpt-5-nano", "temperature": 1.0, "verbosity": "Medium"},
        )
        if created:
            print("new llm_model created")
        return llm_model

    @classmethod
    def get_active_model_params(cls):
        llm_model = cls.get_active_model()
        return llm_model.LLM, llm_model.temperature, llm_model.verbosity

    def __str__(self):
        return f"{self.LLM} | {self.id}"
    
    
    
# Libère le cache pour forcer la mise à jour du system prompt
@receiver([post_save, post_delete], sender=SystemPrompt)
def clear_systemprompt_cache(sender, instance, **kwargs):
    cache.delete("systemprompt_active") 

