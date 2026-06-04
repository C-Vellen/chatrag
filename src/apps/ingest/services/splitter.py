import textwrap
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..models import DocumentRef
from src.settings import DEBUG
from src.utils import get_closest_smaller_index, get_closest_bigger_index

def split_documents(docs: list[Document]) -> list[Document]:
    """
    Découpe les documents en chunks avec RecursiveCharacterTextSplitter.
    
    Args: 
        liste de Document
    
    Returns: 
        liste de chunks avec les metadata (pour chaque chunk):

        - document_id :   identifiant du documentref
        - source :        titre du document
        - source_type:    type du document (TXT, PDF, MD, YT)
        - source_origin:  origine du document : download ou https:// ou src/documents/...
        - source_url:     accès au lien https:// de la source (media ou externe)
        - creattiondate
        - index:          index (numéro d'ordre) du chunk
        - total_index:    nombre total de chunks du document
        - start_index:    index du 1er caractère du chunk
        - end_index:      index du dernier caractère du chunk

        # spécifique aux PDF:
        - total_page:     nombre total de pages
        - page:           index de la page du chunk
        - page_label:     numero de la page du chunk (=index+1)
        - creator:        info sur la création du PDF
        - producer:       info sur la création du PDF

        # spécifique aux videos youtube:
    
        - start_time:     horodatage début du chunk (en s)
        - end_time:       horodatage fin du chunk (en s)
    """
    

    document_id = docs[0].metadata["document_id"]
    documentref = DocumentRef.objects.get(id=document_id)
    collection = documentref.collection
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=collection.chunk_size,
        chunk_overlap=collection.chunk_overlap,
        length_function=len,
        # Séparateurs par ordre de priorité
        separators=["\n\n", "\n", ". ", " ", ""],
        add_start_index=True,   # Ajoute la position d'origine dans les métadonnées

    )
    chunks = splitter.split_documents(docs)
        
    # ajout du nombre de chunks au documentref
    documentref.nb_chunks = len(chunks)
    documentref.save()
    
     # Tri par (page, start_index) pour reconstituer l'ordre naturel
    # page peut être int ou string selon le loader → on force int
    chunks.sort(key=lambda c: (
        int(c.metadata.get("page", 0)),
        int(c.metadata.get("start_index", 0)),
    ))
    
    for index, chunk in enumerate(chunks, start=1):
        
        chunk.metadata["index"] = index
        chunk.metadata["total_index"] = len(chunks)  
        
        if "start_index" in chunk.metadata:
            chunk.metadata["end_index"] = (
                chunk.metadata["start_index"] + len(chunk.page_content)
            )
            timestamp = documentref.timestamp
            if timestamp:
                first_index = get_closest_smaller_index(chunk.metadata["start_index"], timestamp.keys())
                last_index = get_closest_bigger_index(chunk.metadata["end_index"], timestamp.keys())

                chunk.metadata["start_time"] = timestamp[str(first_index)]
                if last_index:
                    chunk.metadata["end_time"] = timestamp[str(last_index)]
    
   
    # Ajout de l'index après tri
    
        
    
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
    
    return chunks