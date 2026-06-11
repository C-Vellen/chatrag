from django.shortcuts import render, get_object_or_404
from django.http import StreamingHttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
        
       

from .models import Conversation
from .services import stream_response, generate_title


def chat_view(request):
    """Affiche l'interface chat"""

    # Nouvelle conversation ou reprise d'une existante
    conversation_id = request.GET.get("conversation_id")
    conversation    = None
    messages        = []
    
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id)
        messages     = conversation.messages.all()
    
    conversations = Conversation.objects.all()[:20]
    
    context = {
        "conversation":  conversation,
        "conversations": conversations,
        "chat_messages": messages,
    }
    
    return render(request, "chat/chat.html", context)


def stream_view(request):
    """Endpoint SSE — retourne la réponse en streaming."""
    if request.method != "POST":
         return HttpResponseNotAllowed(["POST"])

    question        = request.POST.get("question", "").strip()
    conversation_id = request.POST.get("conversation_id", "").strip()

    if not question:
        return HttpResponseBadRequest("question requise")

    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id)
    else:
        conversation = Conversation.objects.create()
        conversation.title = generate_title(question)
        conversation.save()
    
    # collection = Collection.get_active()


    response = StreamingHttpResponse(
        stream_response(conversation.id, question),
        content_type="text/event-stream",
    )
    response["Cache-Control"]  = "no-cache"
    response["X-Accel-Buffering"] = "no"  # désactive le buffering nginx
    
      # Renvoie l'id de la nouvelle conversation dans les headers
    # pour que le JS puisse mettre à jour l'URL
    response["X-Conversation-Id"] = str(conversation.id) 
    response["X-Conversation-Date"] = conversation.created_at.isoformat()
    response["X-Conversation-Title"] = conversation.title
    
    return response


