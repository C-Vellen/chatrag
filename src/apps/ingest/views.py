from django.shortcuts import render, redirect, get_object_or_404
from home.context import usercontext
from .models import Collection, DocumentRef
from .forms import DocumentForm
from .services.ingest import ingest
from .services.inspector import delete_document, list_chunks
from src.config import settings

    
def documents_list(request):
    ''' Liste des documents ingérés + interface pour ingérer un nouveau document'''
    
    
    modeform = True     #affiche le formulaire dans le html
    modechunks = False  #n'affiche pas la liste de chunks dans le formulaire
    
    collection = Collection.get_active()
    context = usercontext(request)
    context.update({
        "title": "Liste des documents ingérés:",    
        "collection_name": collection.collection_name,
        "embedding_model": collection.embedding_model,
        "chunk_size": collection.chunk_size,
        "chunk_overlap": collection.chunk_overlap
    })
    form = DocumentForm()
    
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data.get('file')
            uri = form.cleaned_data.get('uri')
            if file:
                print("> nom fichier: ", file.name)
                ingest(file)
            elif uri:           
                print("> URI : ", uri)
                ingest(uri)
    
            return redirect("ingest:documents_list")
    
    docs = DocumentRef.objects.filter(collection=collection, is_active=True)
    context.update({
        "collection":collection,
        "docs":docs,
        "n_docs":len(docs),
        "form":form,
        "modeform": modeform,
        "modechunks":modechunks,
    })
    
    return render(request, "ingest/list.html", context)
    
    
       
def remove_document(request, document_id):
    """supprime un document:
    - au niveau de la ragdb : supprime tous les chunks de ce document
    - au niveau de la db : supprime l'instance de DocumentRef
    """
    delete_document(document_id)
    DocumentRef.objects.filter(id=document_id).delete()   
    return redirect("ingest:documents_list")
   

def read_chunks(request, document_id):
    ''' Liste des documents ingérés + affichage des chunks du document sélectionné'''

    
    modeform = False     # n'affiche pas le formulaire dans le html
    modechunks = True  # affiche la liste de chunks dans le formulaire
   
    collection = Collection.get_active()  
    context = usercontext(request)
    doc = get_object_or_404(DocumentRef, id=document_id)
    
    chunks = list_chunks(str(document_id))
        
    
    docs = DocumentRef.objects.filter(collection=collection, is_active=True)
    context.update({
        
        "docs":docs,
        "n_docs":len(docs),
        "modeform": modeform,
        "modechunks":modechunks,
        "doc":doc,
        "chunks":[c["content"] for c in chunks]
        
    })
   

    return render(request, "ingest/list.html", context)
  