from dataclasses import dataclass
from langchain_core.documents import Document
from ingest.services.embedder import get_vectorstore
from ingest.models import Collection
from retrieval.models import RetrivConfig


@dataclass
class ChunkResult:
    """Un chunk avec sa métrique de similarité."""
    chunk:       Document
    distance:    float      
    similarity:  float      






def _compute_similarity(distance: float, metric: str) -> float:
    match metric:
        case "COSINE":
            return 1 - distance
        case "EUCLIDEAN":
            return 1 / (1 + distance)
        case "DOT_PRODUCT":
            return -distance
        case _:
            return 1 - distance


def _to_chunk_results(
    docs_with_scores: list[tuple[Document, float]],
    metric: str,
) -> list[ChunkResult]:
    results = [
        ChunkResult(
            chunk=doc,
            distance=round(float(score), 4),
            similarity=round(_compute_similarity(float(score), metric), 4),
        )
        for doc, score in docs_with_scores
    ]
    results.sort(key=lambda r: r.distance)
    return results


def retrieve_chunks(question: str) -> list[ChunkResult]:
    """
    Retourne les chunks les plus pertinents pour une question.
    Les paramètres (k, search_type, etc.) sont lus depuis RetrivConfig.
    """
    collection = Collection.get_active()
    vectorstore = get_vectorstore()
    cfg = RetrivConfig.get_solo()

    match cfg.search_type:

        case "similarity":
            docs_with_scores = vectorstore.similarity_search_with_score(
                question,
                k=cfg.k,
            )

        case "mmr":
            # MMR ne retourne pas de scores → on affecte distance=0 / similarity=1
            docs = vectorstore.max_marginal_relevance_search(
                question,
                k=cfg.k,
                fetch_k=cfg.fetch_k,
                lambda_mult=cfg.lambda_mult,
            )
            docs_with_scores = [(doc, 0.0) for doc in docs]

        case "similarity_score_threshold":
            docs_with_scores = vectorstore.similarity_search_with_relevance_scores(
                question,
                k=cfg.k,
                score_threshold=cfg.score_threshold,
            )

        case _:
            raise ValueError(f"search_type inconnu : {cfg.search_type!r}")

    return _to_chunk_results(docs_with_scores, collection.metrics)













# ========================================
# def retrieve_chunks(question: str, k: int = 4) -> list[ChunkResult]:
#     """
#     Retourne les k chunks les plus pertinents pour une question,
#     avec leur métrique de distance.
#     """
#     collection = Collection.get_active()
#     vectorstore = get_vectorstore()

#     # Retourne une liste de tuples (Document, distance L2)
#     docs_with_scores = vectorstore.similarity_search_with_score(question, k=k)

#     results = []
#     for doc, distance in docs_with_scores:
#         # Calcul de la similarité selon la métrique configurée
#         match collection.metrics:
#             case "COSINE":
#                 similarity = 1 - distance
#             case "EUCLIDEAN":
#                 similarity = 1 / (1 + distance)
#             case "DOT_PRODUCT":
#                 similarity = -distance
        
#         results.append(ChunkResult(
#             chunk      = doc,
#             distance   = round(float(distance), 4),
#             similarity = round(float(similarity), 4),
#         ))

    # Tri par distance croissante (meilleurs en premier)
    results.sort(key=lambda r: r.distance)

    return results


def print_chunks_results(question: str, results: list[ChunkResult]) -> None:
    """Affiche en console les chunks récupérés avec leurs métriques."""
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"🔍 QUESTION : {question}")
    print(f"📚 {len(results)} chunks sélectionnés")
    print(sep)

    for i, result in enumerate(results, 1):
        doc        = result.chunk
        source     = doc.metadata.get("source", "?")
        page       = doc.metadata.get("page", "")
        doc_id     = doc.metadata.get("document_id", "")
        page_str   = f"| page {page}" if page else ""
        doc_str    = f"| doc {str(doc_id)[:8]}..." if doc_id else ""

        print(f"\n  ┌─ Chunk {i} {page_str} {doc_str}")
        print(f"  │  📏 distance L2  : {result.distance}")
        print(f"  │  🎯 similarité   : {result.similarity}")
        print(f"  │  📄 source       : {source}")
        print(f"  │")
        for line in doc.page_content.strip().splitlines():
            print(f"  │  {line}")
        print(f"  └{'─' * 60}")

    print(sep + "\n")