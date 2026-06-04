
from pathlib import Path
from django.core.files.uploadedfile import UploadedFile
from django.core.files.base import ContentFile
from ..models import Collection, DocumentRef
from .loader import load_documents
from .splitter import split_documents
from .embedder import embed_and_store
from src.utils import extract_title, is_youtube_url, parse_uri, iter_uri, get_youtube_script_with_timestamp



def ingest_file(source_origin, file:UploadedFile) -> None:
    """ Ingestion d'un fichier : 
            - création du DocumentRef
            - lancement du pipeline d'ingestion

    Args:
        source_origin: 'download' ou path ou url
        file (UploadFile): fichier à ingérer

    Returns: None
    """
    if isinstance(file, UploadedFile):
        suffix = Path(file.name).suffix.lower()
        if suffix not in (".pdf", ".txt", ".md"):
            raise ValueError(f"Format non supporté : {suffix}")
        
        collection = Collection.get_active()
        documentref = DocumentRef(
            collection=     Collection.get_active(), 
            titre=          extract_title(file.name),
            source_type=    suffix[1:].upper(),
            source_origin=  source_origin,
            source_file=    file,
            )    
        documentref.save()
        
        ingest(documentref)
        
        
def ingest_uri(source_origin: str) -> None:
    """ Ingestion d'un document à partir d'un uri : 
            - création du DocumentRef
            - lancement du pipeline d'ingestion

    Args:
        source_origin: path ou url
        exemples : 
            https://www.youtube.com/watch?v=video_id
            https://www.unsite.com/document.pdf
            src/documents/
            src/documents/document.txt

    Returns: None
    """
    if is_youtube_url(source_origin):
        ingest_video(source_origin)
        
    else:
        source = parse_uri(source_origin)
        
        match source["type"]:
            
            # cas où l'uri est un dossier:
            case "path": 
                # analyse récursive du dossier:
                for result in iter_uri(source["path"]): 
                    if result["type"] == "filepath":
                        ingest_file(result["path"], result["file"])
                    elif result["type"] == "error":
                        pass
            
            # cas où l'uri est un fichier:
            case "filepath":
                ingest_file(source_origin, source["file"])
                
            # cas où l'uri est l'url d'un fichier:
            case "fileurl":
                ingest_file(source_origin, source["file"])
                
            case "error":
                pass
                

def ingest_video(source_origin: str) -> None:
    """ Ingestion d'une video Youtube : 
            - transcription avec horodatage
            - création du DocumentRef
            - lancment du pipeline d'ingestion

    Args:
        source_origin: url de la video

    Returns: None
    """
    videoscript = get_youtube_script_with_timestamp(source_origin)
    
    documentref = DocumentRef(
        collection=     Collection.get_active(), 
        titre=          videoscript["titre"],
        source_type=    "YT",
        source_origin=  source_origin,
        video_id=       videoscript["video_id"],
        timestamp=      videoscript["timestamp"],
        duration =      videoscript["duration"]
        )    
    
    # enregistrement du script dans un fichier:
    temporary_file = ContentFile(videoscript["content"].encode('utf-8')) 
    filename = f"{videoscript["titre"]}.txt"
    documentref.source_file.save(filename, temporary_file, save=True)
    
    ingest(documentref)
    
        
def ingest(documentref: DocumentRef) -> None:
    """Pipeline complète d'ingestion : load -> split → embed → store."""

    print("\n============= Ingestion ==================")
    
    print(f"\n📂 Chargement des documents depuis : {documentref}")
    documents = load_documents(documentref)  
    print(f"  → document chargé")           
        
    print("\n✂️  Découpage en chunks...")
    chunks = split_documents(documents)  
   
    print("\n🔢 Embedding et stockage dans pgvector...")
    embed_and_store(chunks)

    print("\n✅ Ingestion terminée !\n")
    
        
    
        