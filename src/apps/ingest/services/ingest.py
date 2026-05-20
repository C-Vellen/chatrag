
from pathlib import Path
from typing import Union
from django.core.files.uploadedfile import UploadedFile
from .loader import load_documents
from .splitter import split_documents
from .embedder import embed_and_store



def ingest(source: Union[str, Path, UploadedFile, dict]) -> None:
    """Pipeline complète d'ingestion : split → embed → store."""
    
    print("\n============= Ingestion ==================")
    
    print(f"\n📂 Chargement des documents depuis : {source}")
    documents = load_documents(source)
    print(f"  → {len(documents)} document(s) chargé(s)")
    
    print("\n✂️  Découpage en chunks...")
    chunks = split_documents(documents)

    print("\n🔢 Embedding et stockage dans pgvector...")
    embed_and_store(chunks)

    print("\n✅ Ingestion terminée !\n")