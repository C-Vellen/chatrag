import json
from django.http import JsonResponse
from celery.result import AsyncResult
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from apps.special_bridge import has_special, add_documents_from_api
from ingest.models import Collection, DocumentRef, WaitingList
from .forms import DocumentForm
from ingest.services.ingest import add_file, add_uri, ingest #, ingest_file, ingest_uri
from ingest.services.inspector import delete_document, list_chunks, get_ragdb_size
from ingest.tasks import ingest_documents_task
from src.config import settings

    
def documents_list(request):
    """ Liste des documents ingérés + interface pour ingérer un nouveau document"""
    
    collection = Collection.get_active()
    form = DocumentForm()
    task_id = None
    
    if request.method == "POST":
        print("------- POST -----------")
        if 'add-documents' in request.POST:
            print("......add......")
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data.get('file')
                uri = form.cleaned_data.get('uri')
                if file:
                    print("> nom fichier: ", file.name)
                    source_origin = "download"
                    try:
                        titre = add_file(source_origin, file)
                        messages.success(request, f"Nouveau document {titre} ajouté dans la liste")
                    except ValueError as e:
                        print(f"Erreur: {e}")
                        messages.warning(request, f"Erreur: {e}")
                    except Exception as e:
                        messages.error(request, f"Une erreur imprévue est survenue : {e}")
                if uri:           
                    print("> URI : ", uri)
                    try:
                        success_msg = add_uri(uri)
                        messages.success(request, success_msg)
                    except ValueError as e:
                        messages.warning(request, f"Erreur: {e}")
                    except Exception as e:
                        print(f"Erreur: {e}")
                        messages.error(request, f"Erreur: {e}")
                return redirect("ingest_admin:documents_list")
            
            
        elif 'script-documents' in request.POST:
                print("......ingest......")
                form = DocumentForm(request.POST)
                if form.is_valid():
                    docIdList = request.POST.getlist("doc")
                    
                    
                    
        elif 'ingest-documents' in request.POST:
            print("......ingest......")
            form = DocumentForm(request.POST)
            if form.is_valid():
                #----
                docIdList = request.POST.getlist("doc")
                # NOUVELLE VERSION : AVEC task CELERY
                # if docIdList:
                #     print(docIdList)
                #     # .delay() envoie la tâche dans Redis et retourne IMMÉDIATEMENT
                #     # un AsyncResult avec un task_id unique.
                #     # Django n'attend PAS la fin de l'ingestion.
                #     task = ingest_documents_task.delay(docIdList)
                #     task_id = task.id

                #     # Stocke le task_id en session pour le retrouver si l'utilisateur
                #     # navigue et revient sur la page
                #     request.session['ingest_task_id'] = task_id
                
                # ANCIENNE VERSION : APPEL DIRECT A INGESTION
                docs = DocumentRef.objects.filter(id__in=request.POST.getlist("doc"))
                for doc in docs:                    
                    ingest(doc)                   
                #----
                
            elif 'delete-documents' in request.POST:
                print("......delete......")
                form = DocumentForm(request.POST)
                if form.is_valid(): 
                    docIdList = request.POST.getlist("doc")
                        
    
    # Récupère le task_id en session (si ingestion en cours)
    task_id = task_id or request.session.get('ingest_task_id')

    # Détermine si une ingestion est en cours
    ingestion_running = False
    if task_id:
        result = AsyncResult(task_id)
        # PENDING = en attente, PROGRESS = en cours
        ingestion_running = result.state in ('PENDING', 'PROGRESS')
        if result.state == 'SUCCESS':
            # Ingestion terminée → on nettoie la session
            del request.session['ingest_task_id']
            task_id = None
         
                
    
    docs = DocumentRef.objects.filter(collection=collection, is_active=True).order_by("-created_at")       
    
    ingestion_running = False
    docs_stat = DocumentRef.docs_stat()
       
    context = {
        "title": "Liste des documents ingérés:",     
        "collection":collection,
        "docs":docs,
        "docs_stat": DocumentRef.docs_stat(),
        "n_chunks": DocumentRef.objects.aggregate(total=Sum('nb_chunks'))["total"],
        "form":form,
        "db_size": get_ragdb_size(),
        "task_id":           task_id,
        "ingestion_running": ingestion_running,
        "has_special": has_special,
    }
    
    
    return render(request, "ingest_admin/list.html", context)
    
           
def remove_document(request):
    """supprime les documents d'une liste:
    - au niveau de la ragdb : supprime tous les chunks de ce document
    - au niveau de la db : supprime l'instance de DocumentRef
    """
    docs = request.GET.getlist('doc')
    print(docs)
    for doc in DocumentRef.objects.filter(id__in=docs):
        delete_document(doc.id)
        doc.delete()
        

    return redirect("ingest_admin:documents_list")
   
  
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
  


# def waiting_list(request):
#     """ Affiche la liste d'attente des documents """
    
#     if request.method == "POST":
#         ingest_waitingList(request.POST.getlist("doc"))
            
#     docList = WaitingList.objects.all().order_by("-date")
#     context={
#         "text": "Liste des videos",
#         "docList": docList,
#         "n_docs": len(docList),
#         "n_new": len(WaitingList.objects.filter(status="NEW")),
#         "n_reg": len(WaitingList.objects.filter(status="REG")),
#         "n_err": len(WaitingList.objects.filter(status="ERR")),
#     }
        
#     return render(request, "ingest/waiting_list.html", context)


def update_list(request):
    """ Met à jour la liste d'attente à partir d'une API externe"""
    
    add_documents_from_api()
    return redirect("ingest_admin:documents_list")
  