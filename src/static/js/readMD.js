async function selectMarkdown(btn, displayZone) {
  const fileUrl = btn.dataset.file;
  const titre = btn.dataset.titre;
  const startIndex = parseInt(btn.dataset.start);
  const endIndex = parseInt(btn.dataset.end);
  closePlayer();
  closePdf();
  closeTxt();
  closeMd();
  closeChunksList();
  document.querySelectorAll('.headline-title').forEach(d => d.classList.remove('bg-focuscolor-line')); 
  btn.closest('.headline-title').classList.add('bg-focuscolor-line');

  displayZone.querySelector('[data-element="titre"]').textContent = titre;

  const titreIndex = displayZone.querySelector('[data-element="headline"]')
  const container = displayZone.querySelector('[data-element="container"]')

  titreIndex.classList.remove('hidden');
  titreIndex.classList.add('flex');
  container.classList.remove('hidden');
  container.classList.add('flex');

  // Charger le fichier texte brut
  const response = await fetch(fileUrl);
  const text = await response.text();

    console.log("INDEX: ", startIndex, endIndex)
  renderMarkdown(displayZone, text, startIndex, endIndex);
  if (endIndex) {
      displayZone.querySelector('[data-element="indexing"]').textContent = `Index: ${startIndex} → ${endIndex}`;
  }
}

function renderMarkdown(displayZone, text, startIndex, endIndex) {

  const viewer = displayZone.querySelector('[data-element="viewer"]');
  const container = displayZone.querySelector('[data-element="container"]');

  // Construit le HTML à partir du texte brut du fichier markdown
  if (viewer) {
    viewer.innerHTML = marked.parse(text)
  
    // Hauteur du viewer = hauteur d'une "page" lisible, basée sur la fenêtre
    container.style.height = `${window.innerHeight * 0.7}px`;
    // Scroll jusqu'à la surbrillance
    scrollToHighlight(viewer);
  }
}

function scrollToHighlight(viewer) {
  const mark = viewer.querySelector('mark');
  if (!mark) return;

  // Centre l'extrait dans la fenêtre de scroll
  const viewerRect = viewer.getBoundingClientRect();
  const markRect = mark.getBoundingClientRect();
  const offset = markRect.top - viewerRect.top - (viewer.clientHeight / 2) + (markRect.height / 2);
  viewer.scrollTo({
    top: viewer.scrollTop + offset,
    behavior: "smooth"
  }) 
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function closeMd() {
  document.querySelectorAll('[data-block-type="MD"]').forEach(displayZone => { 
    displayZone.querySelector('[data-element="headline"]').classList.add("hidden");
    displayZone.querySelector('[data-element="container"]').classList.add("hidden");
   
    const viewer = displayZone?.querySelector('[data-element="viewer"]');
    if (viewer) {
        viewer.innerHTML = '';
    }
    document.querySelectorAll('.headline-title').forEach(d => d.classList.remove('bg-focuscolor-line'));
  })
}