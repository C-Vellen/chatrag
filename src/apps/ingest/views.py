from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from apps.special_bridge import ingest_waitingList, get_documents_from_api
from .models import Collection, DocumentRef, WaitingList
from .forms import DocumentForm
from .services.ingest import ingest_file, ingest_uri
from .services.inspector import delete_document, list_chunks, get_ragdb_size
from src.settings import HAS_SPECIAL_APP
from src.config import settings

    
def documents_list(request):
    """ Liste des documents ingérés + interface pour ingérer un nouveau document"""
    
    collection = Collection.get_active()
    form = DocumentForm()
    
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data.get('file')
            uri = form.cleaned_data.get('uri')
            if file:
                print("> nom fichier: ", file.name)
                source_origin = "download"
                ingest_file(source_origin, file)
            elif uri:           
                print("> URI : ", uri)
                ingest_uri(uri)
    
            return redirect("ingest:documents_list")
    
    docs = DocumentRef.objects.filter(collection=collection, is_active=True)
    context = {
        "title": "Liste des documents ingérés:",     
        "collection":collection,
        "docs":docs,
        "n_docs":len(docs),
        "n_chunks": DocumentRef.objects.aggregate(total=Sum('nb_chunks'))["total"],
        "form":form,
        "db_size": get_ragdb_size(),
        "has_special": HAS_SPECIAL_APP,
    }
    
    return render(request, "ingest/list.html", context)
    
           
def remove_document(request, document_id):
    """supprime un document:
    - au niveau de la ragdb : supprime tous les chunks de ce document
    - au niveau de la db : supprime l'instance de DocumentRef
    """
    doc = DocumentRef.objects.filter(id=document_id).first()
    video_id = doc.video_id if doc else None
    
    if doc:
        if video_id:
            wdoc = WaitingList.objects.filter(video_id=video_id).first()
            if wdoc:
                wdoc.status = "NEW"
                wdoc.save()
        doc.delete()
    delete_document(document_id)

    return redirect("ingest:documents_list")
   
  
def read_chunks(request, document_id: str): 
    """Renvoie un html de tous les chunks du document sélectionné + surbrillance du chunk sélectionné"""
    
    try:
        chunk_index = int(request.GET.get("chunk", None))
    except ValueError:
        chunk_index = None
        
    doc = get_object_or_404(DocumentRef, id=document_id)
    chunks = list_chunks(str(document_id))
    
    context = {
        "doc":          doc,
        "chunks":       [c["content"] for c in chunks],
        "chunk_index":  chunk_index
    } 

    return render(request, "viewer/chunks_viewer.html", context)
  


def waiting_list(request):
    """ Affiche la liste d'attente des documents """
    
    if request.method == "POST":
        ingest_waitingList(request.POST.getlist("doc"))
            
    docList = WaitingList.objects.all().order_by("-date")
    context={
        "text": "Liste des videos",
        "docList": docList,
        "n_docs": len(docList),
        "n_new": len(WaitingList.objects.filter(status="NEW")),
        "n_reg": len(WaitingList.objects.filter(status="REG")),
        "n_err": len(WaitingList.objects.filter(status="ERR")),
    }
        
    return render(request, "ingest/waiting_list.html", context)


def update_waiting_list(request):
    """ Met à jour la liste d'attente à partir d'une API externe"""
    
    get_documents_from_api()
    return redirect("ingest:waiting_list")
  