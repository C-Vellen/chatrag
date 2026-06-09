from openai import OpenAI
from retrieval.retriever import retrieve_chunks
from .models import Conversation, Message, LLMModel

client = OpenAI()

SYSTEM_PROMPT = """Tu es un assistant expert. Réponds à la question en te basant
uniquement sur le contexte fourni. Si la réponse ne s'y trouve pas, dis-le clairement.
Réponds en français."""


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
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

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