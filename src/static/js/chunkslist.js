
async function selectChunksList(btn) {

    const docId = btn.getAttribute('data-id');
    const baseUrl = btn.getAttribute('data-url');
    const chunkIndex = btn.getAttribute('data-index');
    const chunksUrl = `${baseUrl}?chunk=${chunkIndex}`
    const chunksList = document.getElementById("chunks-list")

    closePlayer()
    closePdf();
    closeTxt();
    document.querySelectorAll('.headline-title').forEach(d => d.classList.remove('bg-focuscolor-line')); 
    btn.closest('.headline-title').classList.add('bg-focuscolor-line');
    try {
        // appel URL de la vue Django fournie par ingest.views.read_chunks
        const response = await fetch(chunksUrl);
        
        if (!response.ok) throw new Error("Erreur lors du chargement des chunks");
        // récupération du contenu et injection dans le conteneur chunkList
        const chunksListContent = await response.text();
        chunksList.innerHTML = chunksListContent
        chunksList.classList.remove('hidden');
    } catch (error) {
        console.error(error);
        chunksList.innerHTML = "<p style='color:red;'>Impossible de charger les chunks.</p>";
        chunksList.classList.remove('hidden');
    }
}

function closeChunksList() {

    chunksList = document.getElementById('chunks-list')
    chunksList.classList.add('hidden')
    chunksList.innerHTML = ''

    document.querySelectorAll('.headline-title').forEach(d => d.classList.remove('bg-focuscolor-line'));


}
