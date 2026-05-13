from django.shortcuts import render
from home.context import usercontext


  


def talk(request):
    '''
    talk with a chatbot using RAG
    '''
    context = usercontext(request)
    context.update({
        "title": "Démarrer une conversation :",        
    })
   
    return render(request, "chat/talk.html", context)
    

