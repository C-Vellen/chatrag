from django.shortcuts import render
from home.context import usercontext

# Create your views here.


def documents_list(request):
    '''
    list ingested documents:
    -> fetch document names from db pg_vector
    -> return a context to template
    '''
    
    context = usercontext(request)
    context.update({
        "title": "Liste des documents ingérés:",        
    })

    
    return render(request, "ingest/list.html", context)
    
    
    
