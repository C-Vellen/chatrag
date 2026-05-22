from dataclasses import dataclass
from langchain_core.documents import Document
from ingest.services.embedder import get_vectorstore


@dataclass
class ChunkResult:
    """Un chunk avec sa métrique de similarité."""
    chunk:       Document
    distance:    float      # distance L2 (plus proche de 0 = plus similaire)
    similarity:  float      # similarité normalisée entre 0 et 1


def retrieve_chunks(question: str, k: int = 4) -> list[ChunkResult]:
    """
    Retourne les k chunks les plus pertinents pour une question,
    avec leur métrique de distance.
    """
    vectorstore = get_vectorstore()

    # Retourne une liste de tuples (Document, distance L2)
    docs_with_scores = vectorstore.similarity_search_with_score(question, k=k)

    results = []
    for doc, distance in docs_with_scores:
        # Normalisation : convertit la distance L2 en similarité [0, 1]
        # Plus la distance est faible, plus la similarité est haute
        similarity = 1 / (1 + distance)

        results.append(ChunkResult(
            chunk      = doc,
            distance   = round(float(distance), 4),
            similarity = round(float(similarity), 4),
        ))

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