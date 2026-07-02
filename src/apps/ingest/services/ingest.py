
from pathlib import Path
from django.core.files.uploadedfile import UploadedFile
from django.core.files.base import ContentFile
from ..models import Collection, DocumentRef
from .loader import load_documents
from .splitter import split_documents
from .embedder import embed_and_store
from src.utils import extract_title, is_youtube_url, parse_uri, iter_uri, get_video_info, get_video_script_and_timestamp, get_youtube_script_with_timestamp



def add_file(source_origin, file:UploadedFile) -> None:
    """ Ajout d'un fichier : 
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
        documentref.status = DocumentRef.Status.NEW
        documentref.save()
        documentref.date = documentref.created_at
        documentref.save()
        return(f"{documentref.titre[:20]}...")
    else:
        raise ValueError("Fichier non téléchargeable")
        
        
def add_uri(source_origin: str) -> None:
    """ Ajout d'un document à partir d'un uri : 
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
        titre_video = add_video(source_origin)
        return f"Document video youtube ajouté : {titre_video[:20]}..."
        
    else:
        source = parse_uri(source_origin)
        n_files = 0
        print("n_files: ", n_files)
        match source["type"]:
            
            # cas où l'uri est un dossier:
            case "path": 
                # analyse récursive du dossier:
                
                for result in iter_uri(source["path"]): 
                    if result["type"] == "filepath":
                        print("n_files: ", n_files)
                        try:
                            add_file(result["path"], result["file"])
                            n_files += 1
                        except Exception:
                            pass
                            
                    elif result["type"] == "error":
                        print(f"{result["reason"]}")

            
            # cas où l'uri est un fichier:
            case "filepath":
                try:
                    add_file(source_origin, source["file"])
                    n_files += 1
                except Exception as e:
                    print(f"Erreur: {e}")
                
            # cas où l'uri est l'url d'un fichier:
            case "fileurl":
                try:
                    add_file(source_origin, source["file"])
                    n_files += 1
                except Exception as e:
                    print(f"Erreur: {e}")
                
            case "error":
                print(f"{source["reason"]}")
                
        return f"Documents ajoutés avec succès: {n_files}"
                

def add_video(source_origin: str) -> None:
    """ Ajout d'une video Youtube : 
            - transcription avec horodatage
            - création du DocumentRef
            - lancment du pipeline d'ingestion

    Args:
        source_origin: url de la video

    Returns: None
    """
    # videoscript = get_youtube_script_with_timestamp(source_origin)
    video_info = get_video_info(source_origin)
    video_id =  video_info["video_id"]
    
    documentref, created = DocumentRef.objects.get_or_create(
        collection=Collection.get_active(),
        video_id=video_id
        )
    
    if created:
        documentref.titre =         video_info["title"]
        documentref.source_type =   "YT"
        documentref.source_origin = source_origin,
        # documentref.timestamp=    videoscript["timestamp"]
        documentref.duration =      video_info["duration"]
        documentref.date =          video_info["date"]
        documentref.save()
        
        # enregistrement du script dans un fichier:
        # temporary_file = ContentFile(videoscript["content"].encode('utf-8')) 
        # filename = f"{videoscript["titre"]}.txt"
        # documentref.source_file.save(filename, temporary_file, save=True)
        
        if not documentref.date:
            documentref.date = documentref.created_at
            documentref.save()
            
        return documentref.titre 
      
    else:
        raise ValueError(f"Video en doublon, déjà ajoutée: {video_id} - {documentref.titre[:20]}...")
   
     
def ingest(doc: DocumentRef | list[DocumentRef]) -> None:
    """Traite l'ingestion d'un document ou d'une liste de documents"""
    
    if isinstance(doc, DocumentRef):
        print(f"\n============= Ingestion du document {doc.titre}==================")
        
        if doc.source_type == "YT":
            # récuparation du script :
            if not doc.source_file or not doc.timestamp:
                
                video_script = get_video_script_and_timestamp(doc.video_id)
                doc.timestamp =  video_script["timestamp"]
                # enregistrement du script dans un fichier:
                temporary_file = ContentFile(video_script["content"].encode('utf-8')) 
                filename = f"{doc.titre}.txt"
                doc.source_file.save(filename, temporary_file, save=True)
            
            
        ingest_pipeline(doc)
        
    elif isinstance(doc, (list, tuple)):
        # Optionnel mais professionnel : on valide que la liste n'est pas vide 
        # et que ses éléments sont bien des instances de Document
        print(f"\n============= Ingestion des {len(doc) } documents ==================")
        for i, item in enumerate(doc):
            
            if not isinstance(item, DocumentRef):
                print(f"Document {i} ne peut pas être ingéré. Type invalide: ({type(item).__name__})")
            
            print(f"\n------------ Ingestion du document {i} :  {doc.titre}  ------------")
            ingest_pipeline(item)
            
    # Cas 3 : Type inconnu, on lève une exception propre
    else:
        raise TypeError(
            f"Argument invalide. Type reçu : '{type(doc).__name__}'. "
            f"Attendu : 'Document' ou 'List[Document]'."
        )
    
    
def ingest_pipeline(documentref: DocumentRef) -> None:
    """Pipeline complète d'ingestion : load -> split → embed → store."""
        
    print(f"\n📂 Chargement des documents depuis : {documentref}")
    documents = load_documents(documentref)  
    print(f"  → document chargé")           

    print("\n✂️  Découpage en chunks...")
    chunks = split_documents(documents)  
    documentref.nb_chunks = len(chunks)
    documentref.save()
    
    for c in chunks:
        print(c.metadata)
   
    print("\n🔢 Embedding et stockage dans pgvector...")
    embed_and_store(chunks)

    documentref.status = DocumentRef.Status.REGISTERED
    documentref.save()

    print("\n✅ Ingestion terminée !\n")
    
    
        