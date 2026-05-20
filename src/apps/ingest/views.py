from django.shortcuts import render
from django.shortcuts import redirect
from home.context import usercontext
from .models import EmbeddingConfig
from .forms import UploadFileForm, UploadDirForm,  UploadVideoForm
from .services.ingest import ingest
from .services.inspector import list_ingested_documents, delete_document, list_chunks
from src.config import settings
from src.utils import video_transcript, extract_title



    
def documents_list(request):
    ''' Liste des documents ingérés + interface pour ingérer un nouveau document'''
    
    config = EmbeddingConfig.get_active()
    context = usercontext(request)
    context.update({
        "title": "Liste des documents ingérés:",    
        "collection_name": config.collection_name,
        "embedding_model": config.embedding_model,
        "chunk_size": config.chunk_size,
        "chunk_overlap": config.chunk_overlap
    })
    
    source = ""
    if request.method == "POST":
        upload = True
        
        fileform = UploadFileForm()
        dirform = UploadDirForm()
        videoform = UploadVideoForm()
        print("="*20)
        print(request.POST)
        print("="*20)
        
        if "submit_file" in request.POST:
            fileform = UploadFileForm(request.POST, request.FILES)
            if fileform.is_valid():
                file = request.FILES["file"]
                print("> nom fichier: ", file.name)
                ingest(file)
        
        elif "submit_dir" in request.POST:
            dirform = UploadDirForm(request.POST)
            if dirform.is_valid():           
                path = request.POST["path"]
                print("> chemin dossier: ", path)
                ingest(path)        
   
        elif "submit_video" in request.POST:
            videoform = UploadVideoForm(request.POST)
            if videoform.is_valid():           
                url = request.POST["url"].split("&")[0]
                print("> url video: ", url)
                # Traitez la vidéo ici
                # mettre le script dans un fichier
                                 
                
    else:
        fileform = UploadFileForm()
        dirform = UploadDirForm()
        videoform = UploadVideoForm()
        
    
    docs = list_ingested_documents()
    docs = extract_title(docs)
    
    
    context.update({
        "docs":docs,
        "n_docs":len(docs),
        "fileform":fileform,
        "dirform":dirform,
        "videoform":videoform,
    })
    
    
    return render(request, "ingest/list.html", context)
    
    
       
def remove_document(request, source):
    
    config = EmbeddingConfig.get_active()
    context = usercontext(request)
    context.update({
        "title": "Liste des documents ingérés:",    
        "collection_name": config.collection_name,
        "embedding_model": config.embedding_model,
        "chunk_size": config.chunk_size,
        "chunk_overlap": config.chunk_overlap
    })
    
    delete_document(source)
    
    fileform = UploadFileForm()
    dirform = UploadDirForm()
    videoform = UploadVideoForm()
        
    
    docs = list_ingested_documents()
    docs = extract_title(docs)
    
    
    context.update({
        "docs":docs,
        "n_docs":len(docs),
        "fileform":fileform,
        "dirform":dirform,
        "videoform":videoform,
    })
    
    return redirect("ingest:documents_list")
    # return render(request, "ingest/list.html", context)
   

def view_document(request, source):
    config = EmbeddingConfig.get_active()  
    context = usercontext(request)
    context.update({
        "title": "Liste des documents ingérés:",    
        "collection_name": config.collection_name,
        "embedding_model": config.embedding_model,
        "chunk_size": config.chunk_size,
        "chunk_overlap": config.chunk_overlap
    })
    return render(request, "ingest/list.html", context)
  