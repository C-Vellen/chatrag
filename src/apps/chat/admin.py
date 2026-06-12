from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import SystemPrompt, LLMModel, Conversation, Message


class AdminURLMixin(object):
    def get_admin_url(self, obj):
        content_type = ContentType.objects.get_for_model(obj.__class__)
        return reverse("admin:tuto_%s_change" % (
            content_type.model),
            args=(obj.id,))


class MessageInline(admin.TabularInline, AdminURLMixin):
    # affiche sous une catégorie ou une TutoBase les tutos qui lui sont liés
    model = Message
    # champs éditables à afficher
    
    fieldsets = [
            (None, {'fields': ['id', 'role', 'content', 'created_at']})
            ]
    # champs non modifiables à afficher
    readonly_fields = ['id', 'role', 'created_at']
    ordering = ('created_at',)
    extra = 0
    
    # méthode pour pouvoir afficher le lien html des messages :
    def message_link(self, message):
        url = self.get_admin_url(message)
        return mark_safe("<a href='{}'>{}</a>".format(url, message.id))

    message_link.short_description = "lien"




@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):

    # affichage des libellés
    list_display = ["title", "user", "created_at", "updated_at", ]
    readonly_fields = ['created_at', 'updated_at']
    inlines=[MessageInline,]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    # affichage des libellés
    list_display = ["id", "conversation", "role", "content", "created_at"]
    readonly_fields = ["id", "conversation", "role",'created_at']


@admin.register(LLMModel)
class LLMModelAdmin(admin.ModelAdmin):

    # affichage des libellés
    list_display = ["id", "LLM", "temperature", "verbosity", "active"]


@admin.register(SystemPrompt)
class SystemPromptAdmin(admin.ModelAdmin):

    # affichage des libellés
    list_display = ["id", "prompt", "active"]

