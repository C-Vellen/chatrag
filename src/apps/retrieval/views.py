from django.shortcuts import render
from home.context import usercontext
from .retriever import retrieve_chunks, print_chunks_results


def search(request):
    '''
    get closest chunks from DB pg_vector
    '''
    context = usercontext(request)
    context.update({
        "title": "Entrer une question et chercher les extraits les plus pertinents",        
    })
    if request.method == "POST":
        prompt = request.POST["prompt"]
        
        # Récupérer les k meilleurs chunks avec leurs métriques
        results = retrieve_chunks(prompt)

        # Affichage console debug
        print_chunks_results(prompt, results)

        context.update({
            "prompt": prompt,
            "results": results
        })
            
    return render(request, "retrieval/search.html", context)


def read_chunks(request, document_id, chunk_id):
    ''' Affichage des chunks du document sélectionné + surbrillance du chunk sléectionné'''

    
    pass