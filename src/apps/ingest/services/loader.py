from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from ..models import DocumentRef

    
def load_documents(documentref: DocumentRef) -> list[Document]:
    """
    Créé un objet Document depuis un objet DocumentRef
    
    Args:
        documentref avec les champs:
        - id :              identifiant du documentref
        - source :          titre du document
        - source_type:      type du document (TXT, PDF, MD, YT)
        - source_origin:    origine du document : download ou https:// ou src/documents/...
        - source_url:       accès au lien https:// de la source (media ou externe)
        - source_file:      fichier PDF ou TXT (contenu du document)
        - creattiondate
        [champs facultatives]
        - video_id:         identifiant youtube
        - "timestamp":      dictionnaire horodatage {index: starttime} si le "content" provient d'une video
         
    Returns: 
        objet "Document" contenant le texte de source_file du document et les metadonnées:
        - doc.metadata[ "document-id"]:     identifiant du documentref
        - doc.metadata["source"]:           titre du document
        - doc.metadate["source_type"]:      type du document (TXT, PDF, MD, YT)
        - doc.metadate["source_origin"]:    origine du document : download ou https:// ou src/documents/...
        - doc.metadate["video_id"]:         null ou identifiant youtube
    """
    filepath = Path(documentref.source_file.path)
    if documentref.source_type == "PDF":
        docs = PyPDFLoader(filepath).load()
    else:
        docs = TextLoader(filepath).load()
        
    for doc in docs:    
        doc.metadata["document_id"] = str(documentref.id)
        doc.metadata["source"] = documentref.titre
        doc.metadata["source_type"] = documentref.source_type
        doc.metadata["source_origin"] = documentref.source_origin
        doc.metadata["source_url"] = documentref.source_url
        doc.metadata["video_id"] = documentref.video_id
        
    return docs        
    
    