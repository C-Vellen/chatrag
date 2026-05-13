from django.shortcuts import render
from home.context import usercontext


  


def get_chunks(request):
    '''
    get closest chunks from DB pg_vector
    '''
    context = usercontext(request)
    context.update({
        "title": "Entrer une question et chercher les extraits les plus pertinents",        
    })

    
    return render(request, "retrieval/chunks_list.html", context)
    
