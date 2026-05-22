from pathlib import Path
from typing import Union
from django.core.files.uploadedfile import UploadedFile
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain_core.documents import Document
from src.utils import is_youtube_url, video_transcript, extract_title
from ..models import Collection, DocumentRef
import tempfile
import os

"""
- identifie les sources suivant leur origine : fichier, chemin, lien youtube, dictionnaire
- enregistre les sources dans un objet 
"""


def load_from_path(source: str | Path) -> list[Document]:
    """Charge depuis un chemin fichier ou dossier."""
    source = Path(source)
    
    if source.is_dir():
        loaders = [
            DirectoryLoader(str(source), glob="**/*.pdf", loader_cls=PyPDFLoader),
            DirectoryLoader(str(source), glob="**/*.txt", loader_cls=TextLoader),
            DirectoryLoader(str(source), glob="**/*.md",  loader_cls=TextLoader),
        ]
        docs = []
        for loader in loaders:
            docs.extend(loader.load())
            
    
    else:
        
        suffix = source.suffix.lower()
        if suffix == ".pdf":
            docs = PyPDFLoader(str(source)).load()
        elif suffix in (".txt", ".md"):
            docs = TextLoader(str(source)).load()
        else:
            raise ValueError(f"Format non supporté : {suffix}")
        
    collection = Collection.get_active()
    for doc in docs:
        uri = doc.metadata["source"]
        titre = extract_title(uri)
        documentref = DocumentRef(
            collection=collection, 
            titre=titre, 
            source_uri=uri
            )    

        suffix = Path(uri).suffix.lower()
        if suffix in (".pdf", ".txt", ".md"):
            documentref.type_source = suffix[1:3].upper() + "P" 
        else:  
            documentref.type_source = "OTH"
        documentref.save()
        doc.metadata["document_id"] = str(documentref.id)
        doc.metadata["source"] = titre
        
    return docs





def load_from_upload(file: UploadedFile) -> list[Document]:
    """
    Charge depuis un objet UploadedFile Django.
    Ecrit temporairement le fichier sur disque car les loaders
    LangChain ont besoin d'un chemin fichier.
    """
    suffix = Path(file.name).suffix.lower()

    if suffix not in (".pdf", ".txt", ".md"):
        raise ValueError(f"Format non supporté : {suffix}")
    
    titre = extract_title(file.name)
    
    collection = Collection.get_active()
    documentref = DocumentRef(
        collection=collection, 
        titre=titre, 
        source_file=file
        )    
    if suffix in (".pdf", ".txt", ".md"):
        documentref.type_source = suffix[1:3].upper() + "F" 
    else:  
        documentref.type_source = "OTH"
        
    documentref.save()
         
    # Ecriture dans un fichier temporaire
    with tempfile.NamedTemporaryFile(
        suffix=suffix,
        delete=False
    ) as tmp:
        for chunk in file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name
    
    try:
        if suffix == ".pdf":
            
            docs = PyPDFLoader(tmp_path).load()
        else:
            docs = TextLoader(tmp_path).load()
        
        # Remplacer le chemin temporaire par le nom original dans les métadonnées
        for doc in docs:
            doc.metadata["document_id"] = str(documentref.id)
            doc.metadata["source"] = titre
            
            

    finally:
        os.unlink(tmp_path)  # supprime le fichier temporaire dans tous les cas

    return docs



def load_from_video_yt(source: str) -> dict:
    """
    Charge depuis un lien youtube, effectue la transcription
    """
    transcript = video_transcript(source)
    transcript.update({"source_uri":source})
    return transcript


def load_from_dict(data: dict) -> list[Document]:
    """
    Charge depuis un dictionnaire avec les clés :
      - "titre"   : titre du document (utilisé dans les métadonnées)
      - "content" : contenu texte du document
    """
    if "content" not in data:
        raise ValueError("Le dictionnaire doit contenir la clé 'content'.")
    if "titre" not in data:
        raise ValueError("Le dictionnaire doit contenir la clé 'titre'.")

    titre   = data["titre"]
    content = data["content"]

    if not content.strip():
        raise ValueError(f"Le contenu de '{titre}' est vide.")

    collection = Collection.get_active()
    documentref = DocumentRef(
        collection=collection, 
        titre=titre, 
        type_source = "YTU",
        source_uri=data["source_uri"]
        )           
    documentref.save()


    # Ecriture dans un fichier temporaire .txt
    with tempfile.NamedTemporaryFile(
        suffix=".txt",
        delete=False,
        mode="w",
        encoding="utf-8"
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        docs = TextLoader(tmp_path, encoding="utf-8").load()

        # Remplacer les métadonnées avec le titre fourni
        for doc in docs:
            doc.metadata["document_id"] = str(documentref.id)
            doc.metadata["source"] = titre
           
    finally:
        os.unlink(tmp_path)

    return docs




def load_documents(source: Union[UploadedFile, str]) -> list[Document]:
    """
    Point d'entrée unique — accepte :
      - un chemin string ou Path (fichier ou dossier)
      - un UploadedFile Django
      - un str:  URI fichier ou dossier ou video yt
    """
    if isinstance(source, UploadedFile):
        return load_from_upload(source)
    elif is_youtube_url(source):
        transcript = load_from_video_yt(source)
        return load_from_dict(transcript)
    else:
        return load_from_path(source)