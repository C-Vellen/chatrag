from sqlalchemy import create_engine, text
from src.config import settings


def list_ingested_documents() -> list[dict]:
    """
    Retourne la liste des documents ingérés avec leurs métadonnées.
    Se base sur le champ 'source' de cmetadata (chemin du fichier).
    """
    engine = create_engine(settings.ragdb_url)

    query = text("""
        SELECT
            cmetadata->>'source'                    AS source,
            COUNT(*)                                AS nb_chunks,
            MIN(cmetadata->>'page')::int            AS page_min,
            MAX(cmetadata->>'page')::int            AS page_max
        FROM langchain_pg_embedding
        WHERE cmetadata->>'source' IS NOT NULL
        GROUP BY cmetadata->>'source'
        ORDER BY source
    """)

    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()

    return [dict(row) for row in rows]


def print_ingested_documents() -> None:
    """Affiche en console les documents ingérés."""
    docs = list_ingested_documents()

    if not docs:
        print("Aucun document ingéré.")
        return

    sep = "=" * 60
    print(f"\n{sep}")
    print(f"📚 DOCUMENTS INGÉRÉS ({len(docs)} fichier(s))")
    print(sep)

    for doc in docs:
        source = doc["source"]
        title  = source.split("/")[-1]          # nom du fichier seul
        chunks = doc["nb_chunks"]
        pages  = f"pages {doc['page_min']}→{doc['page_max']}" if doc["page_min"] else ""
        print(f"  • {title:<40} {chunks:>4} chunks   {pages}")

    print(sep + "\n")
    
    
def list_collections() -> None:
    engine = create_engine(settings.ragdb_url)
    query = text("""
        SELECT 
            c.name                  AS collection,
            COUNT(e.id)             AS nb_chunks,
            vector_dims(e.embedding) AS dimensions
        FROM langchain_pg_collection c
        JOIN langchain_pg_embedding e ON e.collection_id = c.uuid
        GROUP BY c.name, vector_dims(e.embedding)
        ORDER BY c.name
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()

    print("\n📦 COLLECTIONS PGVECTOR")
    print("=" * 50)
    for row in rows:
        print(f"  • {row['collection']:<35} {row['nb_chunks']:>5} chunks   dim={row['dimensions']}")
    print("=" * 50 + "\n")
    
    
def list_chunks(document_id: str) -> list[dict]:
    """
    Retourne tous les chunks d'un document donné (identifié par son 'source').
    """
    engine = create_engine(settings.ragdb_url)
    query = text("""
        SELECT
            id,
            document                            AS content,
            cmetadata->>'source'                AS source,
            cmetadata->>'page'                  AS page,
            (cmetadata->>'index')::int          AS index,
            (cmetadata->>'start_index')::int    AS start_index,
            (cmetadata->>'end_index')::int      AS end_index
        FROM langchain_pg_embedding
        WHERE cmetadata->>'document_id' = :document_id
        ORDER BY 
             CASE
                WHEN cmetadata->>'index' IS NOT NULL
                    THEN (cmetadata->>'index')::int
                WHEN cmetadata->>'start_index' IS NOT NULL
                    THEN (cmetadata->>'start_index')::int
                ELSE NULL
            END ASC NULLS LAST
    """)
    with engine.connect() as conn:
        rows = conn.execute(query, {"document_id": document_id}).mappings().all()

    if not rows:
        print(f"Aucun chunk trouvé pour le document '{document_id}'.")
        return []

    return [dict(row) for row in rows]

    
def delete_document(document_id: str) -> int:
    """
    Supprime tous les chunks d'un document donné de pgvector.
    Retourne le nombre de chunks supprimés.
    """
    document_id = str(document_id)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print("> document_id: ", document_id, type(document_id))
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    engine = create_engine(settings.ragdb_url)

    # Vérification préalable
    count_query = text("""
        SELECT COUNT(*) AS nb
        FROM langchain_pg_embedding
        WHERE cmetadata->>'document_id' = :document_id
    """)
    delete_query = text("""
        DELETE FROM langchain_pg_embedding
        WHERE cmetadata->>'document_id' = :document_id
    """)

    with engine.begin() as conn:  # begin() = commit automatique
        nb = conn.execute(count_query, {"document_id": document_id}).scalar()

        if nb == 0:
            print(f"⚠️  Aucun chunk trouvé pour '{document_id}'. Rien à supprimer.")
            return 0

        conn.execute(delete_query, {"document_id": document_id})

    print(f"🗑️  {nb} chunk(s) supprimé(s) pour le document '{document_id}'.")
    return nb


def get_ragdb_size() -> str:
    """Retourne la taille de la base ragdb en unité lisible (Ko, Mo, Go)."""
    engine = create_engine(settings.ragdb_url)

    query = text("SELECT pg_database_size(current_database()) AS size_bytes")

    with engine.connect() as conn:
        size_bytes = conn.execute(query).scalar()

    return _format_size(size_bytes)


def _format_size(size_bytes: int) -> str:
    """Convertit des octets en unité lisible."""
    if size_bytes >= 1024 ** 3:
        return f"{size_bytes / 1024 ** 3:.2f} Go"
    elif size_bytes >= 1024 ** 2:
        return f"{size_bytes / 1024 ** 2:.2f} Mo"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} Ko"
    else:
        return f"{size_bytes} octets"
