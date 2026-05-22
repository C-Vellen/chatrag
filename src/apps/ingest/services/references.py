import uuid
from collections import Counter
from django.core.files.uploadedfile import UploadedFile
from ..models import Collection, DocumentRef



"""
module des fonctions callback qui sont appelées pendant la création des documents de la ragdb
et qui permettent de crééer et mettre à jour les DocumenRef.
"""


def create_documentref(titre: str, type_source: str, source_uri: str = "#", file: UploadedFile | None = None ) -> uuid : 
    """ Création des DocumentRef, appelé par le loader"""
    collection = Collection.get_active()
    documentref = DocumentRef(
        collection=collection, 
        titre=titre, 
        type_source=type_source
        )    
    if source_uri:
        documentref.source_uri = source_uri
    if file:
        documentref.source_file = file
        
    documentref.save()
    return documentref.id


def update_documentref(chunks_per_doc: Counter) -> None:
    """ Mise à jour des DocumentRef avec le nombre de chunks, appelé par le splitter """
    for document_id, nb_chunks in chunks_per_doc.items():
        print(">>>>>>>>>>>>>>>>>>>>>> nb_chunks:", document_id, nb_chunks)
        DocumentRef.objects.filter(id=document_id).update(nb_chunks=nb_chunks)
    
    
