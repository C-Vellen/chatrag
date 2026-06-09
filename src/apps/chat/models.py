import uuid
from django.db import models


class Conversation(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title      = models.CharField(max_length=255, blank=True, default="")

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
            defaults={"LLM": "gpt-5-nano", "temperature": 0.2, "verbosity": "Medium"},
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