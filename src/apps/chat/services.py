from openai import OpenAI
from retrieval.retriever import retrieve_chunks
from .models import SystemPrompt, Conversation, Message, LLMModel

client = OpenAI()


def build_context(question: str) -> tuple[str, list]:
    """Récupère les chunks pertinents et construit le contexte."""
    results = retrieve_chunks(question)

    context_parts = []
    chunks_meta   = []

    for r in results:
        source = r.chunk.metadata.get("source", "?")
        page   = r.chunk.metadata.get("page", "")
        page_str = f" p.{page}" if page else ""

        context_parts.append(
            f"[Source: {source}{page_str} | similarité: {r.similarity}]\n"
            f"{r.chunk.page_content}"
        )
        chunks_meta.append({
            "source":      source,
            "page":        page,
            "similarity":  r.similarity,
            "distance":    r.distance,
            "document_id": r.chunk.metadata.get("document_id", ""),
        })

    return "\n\n---\n\n".join(context_parts), chunks_meta


def build_messages(conversation: Conversation, question: str, context: str) -> list:
    """Construit la liste de messages pour l'API OpenAI avec historique."""
    
    system_prompt = SystemPrompt.get_active()
    messages = [{"role": "system", "content": system_prompt.prompt}]

    # Historique de la conversation
    for msg in conversation.messages.all():
        messages.append({"role": msg.role, "content": msg.content})

    # Nouveau message avec contexte RAG
    user_content = f"""Contexte :\n{context}\n\nQuestion : {question}"""
    messages.append({"role": "user", "content": user_content})

    return messages


def stream_response(conversation_id: str, question: str):
    """
    Générateur SSE :
    - récupère les chunks
    - appelle OpenAI en streaming
    - yield chaque token
    - sauvegarde en base à la fin
    """
    conversation = Conversation.objects.get(id=conversation_id)
    
    # if not conversation.messages.exists():
    #     conversation.title = generate_title_with_llm(question)
    #     conversation.save()
        


    # 1. Retrieval
    context, chunks_meta = build_context(question)

    # 2. Sauvegarde du message utilisateur
    Message.objects.create(
        conversation = conversation,
        role         = "user",
        content      = question,
    )

    # 3. Appel OpenAI en streaming
    messages = build_messages(conversation, question, context)
    
    llm = LLMModel.get_active_model()

    full_response = ""

    try:
        stream = client.chat.completions.create(
            model       = llm.LLM,  # ex: "gpt-4o-mini"
            messages    = messages,
            temperature = llm.temperature,
            stream      = True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full_response += delta
                # Format SSE : "data: <token>\n\n"
                yield f"data: {delta}\n\n"

    finally:
        # 4. Sauvegarde de la réponse complète en base
        if full_response:
            Message.objects.create(
                conversation = conversation,
                role         = "assistant",
                content      = full_response,
                chunks_used  = chunks_meta,
            )
        # Signal de fin au client
        yield "data: [DONE]\n\n"
        
        
        
def generate_title(question: str) -> str:
    """génère un titre court."""
    return question[:60]
    
    # tentative de générer le titre avec un LLM :
    # llm = LLMModel.get_active_model()
    # try: 
    #     response = client.chat.completions.create(
    #         model      = llm.LLM,
    #         max_completion_tokens = 100,
    #         messages              = [
    #             {
    #                 "role":    "user",
    #                 "content": f"Génère un titre de 5 mots maximum pour cette question : {question}\nRéponds uniquement avec le titre, rien d'autre."
    #             }
    #         ]
    #     )
    #     title = response.choices[0].message.content.strip()
    #     print(f"DEBUG repr : {repr(title)}")
    #     print(f"DEBUG finish_reason : {response.choices[0].finish_reason}")
    #     return title if title else question[:60]   # fallback si vide
    # except Exception as e:
    #     print(f"DEBUG erreur generate_title : {e}")
    #     return question[:60]   # fallback
    