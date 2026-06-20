var txtDoc = null;

async function selectText(btn, displayZone) {
  const fileUrl = btn.dataset.file;
  const titre = btn.dataset.titre;
  const startIndex = parseInt(btn.dataset.start);
  const endIndex = parseInt(btn.dataset.end);
  closePlayer();
  closePdf();
  closeTxt();
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

  // Charger le fichier texte
  const response = await fetch(fileUrl);
  const text = await response.text();

    console.log("INDEX: ", startIndex, endIndex)
  renderText(displayZone, text, startIndex, endIndex);
  if (endIndex) {
      displayZone.querySelector('[data-element="indexing"]').textContent = `Index: ${startIndex} → ${endIndex}`;
  }
}

function renderText(displayZone, text, startIndex, endIndex) {
  const viewer = displayZone.querySelector('[data-element="viewer"]');
  const container = displayZone.querySelector('[data-element="container"]');

  // Découpe le texte en 3 parties : avant, extrait, après
  const before = text.slice(0, startIndex);
  const extract = text.slice(startIndex, endIndex);
  const after = text.slice(endIndex);

  // Construit le HTML avec la surbrillance
  if (viewer) {
    viewer.innerHTML =
      escapeHtml(before) +
      `<mark class="bg-focuscolor-line text-gray-900 rounded px-0.5">${escapeHtml(extract)}</mark>` +
      escapeHtml(after);
  
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

function closeTxt() {
  document.querySelectorAll('[data-block-type="TXT"]').forEach(displayZone => { 
    displayZone.querySelector('[data-element="headline"]').classList.add("hidden");
    displayZone.querySelector('[data-element="container"]').classList.add("hidden");
   
    const viewer = displayZone?.querySelector('[data-element="viewer"]');
    if (viewer) {
        viewer.innerHTML = '';
    }
    document.querySelectorAll('.headline-title').forEach(d => d.classList.remove('bg-focuscolor-line'));
  })
}