from django.shortcuts import render, get_object_or_404
from django.http import StreamingHttpResponse

from .models import Conversation
from .services import stream_response


def chat_view(request):
    """Affiche l'interface chat et crée une nouvelle conversation si besoin."""

    # Nouvelle conversation ou reprise d'une existante
    conversation_id = request.GET.get("conversation_id")
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id)
    else:
        conversation = Conversation.objects.create()

    conversations = Conversation.objects.all()[:20]
    
    context = {
        "conversation":  conversation,
        "conversations": conversations,
        "messages":      conversation.messages.all(),
    }

    return render(request, "chat/chat.html", context)


def stream_view(request):
    """Endpoint SSE — retourne la réponse en streaming."""
    if request.method != "POST":
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(["POST"])

    question        = request.POST.get("question", "").strip()
    conversation_id = request.POST.get("conversation_id")

    if not question or not conversation_id:
        from django.http import HttpResponseBadRequest
        return HttpResponseBadRequest("question et conversation_id requis")


    response = StreamingHttpResponse(
        stream_response(conversation_id, question),
        content_type="text/event-stream",
    )
    response["Cache-Control"]  = "no-cache"
    response["X-Accel-Buffering"] = "no"  # désactive le buffering nginx
    return response