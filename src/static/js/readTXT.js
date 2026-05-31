var txtDoc = null;

async function selectText(btn) {
  const fileUrl = btn.dataset.file;
  const titre = btn.dataset.titre;
  const startIndex = parseInt(btn.dataset.start);
  const endIndex = parseInt(btn.dataset.end);
  closePlayer()
  closePdf()
  document.querySelectorAll('.chunk-title').forEach(d => d.classList.remove('bg-blue-100')); 
  btn.closest('.chunk-title').classList.add('bg-blue-100');

  document.getElementById('txt-titre').textContent = titre;

  const titreIndex = document.getElementById('txt-titre-index')
  const viewer = document.getElementById('txt-viewer');

  titreIndex.classList.remove('hidden');
  titreIndex.classList.add('flex');
  viewer.classList.remove('hidden');
  viewer.classList.add('flex');

  // Charge le fichier texte
  const response = await fetch(fileUrl);
  const text = await response.text();

  renderText(text, startIndex, endIndex);
  document.getElementById('start-index').textContent = startIndex;
  document.getElementById('end-index').textContent = endIndex;

}

function renderText(text, startIndex, endIndex) {
  const container = document.getElementById('txt-container');
  const viewer = document.getElementById('txt-viewer');
  

  // Découpe le texte en 3 parties : avant, extrait, après
  const before = text.slice(0, startIndex);
  const extract = text.slice(startIndex, endIndex);
  const after = text.slice(endIndex);

  // Construit le HTML avec la surbrillance
  container.innerHTML =
    escapeHtml(before) +
    `<mark class="bg-yellow-200 text-gray-900 rounded px-0.5">${escapeHtml(extract)}</mark>` +
    escapeHtml(after);

  // Hauteur du viewer = hauteur d'une "page" lisible, basée sur la fenêtre
  
  viewer.style.height = `${window.innerHeight * 0.7}px`;

  // Scroll jusqu'à la surbrillance
  scrollToHighlight();
}

function scrollToHighlight() {
  const container = document.getElementById('txt-container');
  const mark = container.querySelector('mark');
  if (!mark) return;

  // Centre l'extrait dans la fenêtre de scroll
  const containerRect = container.getBoundingClientRect();
  const markRect = mark.getBoundingClientRect();
  const offset = markRect.top - containerRect.top - (container.clientHeight / 2) + (markRect.height / 2);
  container.scrollTop += offset;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function closeTxt() {
  const titreIndex = document.getElementById('txt-titre-index')
  const viewer = document.getElementById('txt-viewer');

  titreIndex.classList.add('hidden');
  titreIndex.classList.remove('flex');
  viewer.classList.add('hidden');
  viewer.classList.remove('flex');
  document.getElementById('txt-container').innerHTML = '';
}