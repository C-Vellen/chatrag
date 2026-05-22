import os
import textwrap
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..models import Collection, DocumentRef
from src.config import settings
from src.settings import DEBUG

def split_documents(documents: list[Document]) -> list[Document]:
    """
    Découpe les documents en chunks avec RecursiveCharacterTextSplitter.
    """
    collection = Collection.get_active()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=collection.chunk_size,
        chunk_overlap=collection.chunk_overlap,
        length_function=len,
        # Séparateurs par ordre de priorité
        separators=["\n\n", "\n", ". ", " ", ""],
        add_start_index=True,   # Ajoute la position d'origine dans les métadonnées
    )
    chunks = splitter.split_documents(documents)
    
    # affichage chunk en console:
    if DEBUG:
        if chunks:
            # console_width = os.get_terminal_size().columns - 10
            print(f"\tPremiers chunks sur {len(chunks)}")
            for i, chunk in enumerate(chunks[:3]):
                doc_source = chunk.metadata.get("source", "inconnu").split('/')[-1]
                text = chunks[i].page_content
                formatted_text = textwrap.fill(text, initial_indent="\t", subsequent_indent="\t")
                print(f"\n\t> Document: {doc_source} / chunk: {i+1} ({len(text)} caractères)\n{formatted_text}")
            print(f"\n\t> Document: {doc_source} / chunk: {i+2} ({len(text)} caractères)\n{formatted_text[:100]} ...")
        else:
            print(f"\tAucun chunk")
    print(f"\n  → {len(documents)} document(s) découpés en {len(chunks)} chunks")
    
    return chunks