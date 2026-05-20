import numpy as np
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_postgres import PGVector
from ..models import EmbeddingConfig
from src.config import settings
from src.settings import DEBUG

config = EmbeddingConfig.get_active()

def get_openAI_embeddings() -> OpenAIEmbeddings:
    """
    embeddings avec openAI 
    """
    return OpenAIEmbeddings(
        model=config.embedding_model,
        # dimensions=config.model_dimensions,
        api_key=settings.openai_api_key
    )

def get_hf_embeddings() -> OpenAIEmbeddings:
    """
    embeddings avec hugging-face 
    """
    return OpenAIEmbeddings(
        openai_api_base=f"{settings.embedding_api_url}/v1",
        openai_api_key="none", 
        model=config.embedding_model,
        check_embedding_ctx_length=False,
        chunk_size=config.chunk_number
    )

def get_vectorstore_explicit(chunks):
    """Retourne les vecteurs en permettant leur capture pour debug
        Choisir entre : 
        embeddings=get_openAI_embeddings()
        ou
        embeddings=get-hf-embeddings()
    """
    embeddings = get_hf_embeddings()
    texts = [doc.page_content for doc in chunks]
    metadatas=[d.metadata for d in chunks]

    # Créer les vecteurs explicitement
    vectors = embeddings.embed_documents(texts)
    print("\t > 5 premiers Embeddings:---------------------------------")
    print("\tVecteur | Dimension |      Norme |  vecteur")
    for i, vec in enumerate(vectors[:5]):
        print(f"\t    {i:03d} | {len(vec):>9} | {np.linalg.norm(vec):>10.7f} | [{','.join(f'{v:4f}' for v in vec[:5])}, ...]")
    
    vectorstore = PGVector(
        embeddings=embeddings,
        collection_name=config.collection_name,
        connection=settings.ragdb_url,
        # Crée la table + l'extension pgvector si elle n'existe pas
        create_extension=True,
    )
    # Enregistre les données dans la table:
    vectorstore.add_embeddings(
        texts=texts,
        embeddings=vectors,
        metadatas=metadatas
    )
    
    return texts, vectors


def get_vectorstore() -> PGVector:
    """Retourne le vectorstore connecté à PostgreSQL."""
  
    return PGVector(
        embeddings=get_hf_embeddings(),
        collection_name=config.collection_name,
        connection=settings.ragdb_url,
        # Crée la table + l'extension pgvector si elle n'existe pas
        create_extension=True,
    )

def embed_and_store(chunks: list[Document]) -> PGVector:
    """Calcule les embeddings et stocke les chunks dans pgvector."""
    print(f"  → Calcul des embeddings pour {len(chunks)} chunks...")
    if DEBUG:    
        # Option debuggage: capture des embeddings avant chargement dans la BD
        vectorstore = get_vectorstore_explicit(chunks)
    else:       
        # Option production: chargement direct des embeddings dans la BD
        vectorstore = get_vectorstore()
        vectorstore.add_documents(chunks)
    
    print(f"  → {len(chunks)} chunks et vecteurs stockés dans PostgreSQL {settings.ragdb_name}/{settings.ragdb_user}@localhost:{settings.ragdb_port} ✓")
    return vectorstore

def embed_dryrun(chunks: list[Document]):
    """Dryrun embeddings """
    print(f"  → Calcul des embeddings pour {len(chunks)} chunks...")
    print(repr(settings.ragdb_url))
    print("  → Chunks non stockés dans PostgreSQL ✓")
    