pdfjsLib.GlobalWorkerOptions.workerSrc = PDF_WORKER_URL;

var pdfDoc = null;
var currentPage = 1;

async function selectPdf(btn, displayZone) {
  const fileUrl = btn.dataset.file;
  const titre = btn.dataset.titre;
  const targetPage = parseInt(btn.dataset.page) || 1;
  closePdf();
  closePlayer();
  closeTxt();
  closeChunksList();
  document.querySelectorAll('.headline-title').forEach(d => d.classList.remove('bg-focuscolor-line')); 
  btn.closest('.headline-title').classList.add('bg-focuscolor-line');
 
  displayZone.querySelector('[data-element="titre"]').textContent = titre;

  const titrePagination = displayZone.querySelector('[data-element="headline"]')
  const container = displayZone.querySelector('[data-element="container"]')

  titrePagination.classList.remove("hidden");
  titrePagination.classList.add("flex");
  container.classList.remove("hidden");
  container.classList.add("flex");
  

  pdfDoc = await pdfjsLib.getDocument(fileUrl).promise;
  displayZone.querySelector('[data-element="total-pages"]').textContent = pdfDoc.numPages;

  await renderAllPages(displayZone);
  scrollToPage(displayZone, targetPage);
  window.scrollTo({top: 0, behavior: "smooth"});
}

async function renderAllPages(displayZone) {

  const viewer = displayZone.querySelector('[data-element="viewer"]');
  const container = displayZone.querySelector('[data-element="container"]');

  viewer.innerHTML = '';

  for (let i = 1; i <= pdfDoc.numPages; i++) {
    const page = await pdfDoc.getPage(i);
    const naturalViewport = page.getViewport({ scale: 1 });


    // Calcule le scale pour que la page remplisse exactement la largeur du viewer
    // (32px = padding p-4 × 2 côtés)
    const availableWidth = viewer.clientWidth - 32;
    const scale = availableWidth / naturalViewport.width;
    const viewport = page.getViewport({ scale });


    // Après la première page, fixe la hauteur du container = hauteur d'une page + header
    if (i === 1) {
      container.style.height = `${viewport.height + 32}px`;
    }

    const wrapper = document.createElement('div');
    wrapper.id = `page-wrapper-${i}`;
    wrapper.className = 'w-full';

    const canvas = document.createElement('canvas');
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    canvas.className = 'w-full shadow-md';

    wrapper.appendChild(canvas);
    viewer.appendChild(wrapper);

    await page.render({ canvasContext: canvas.getContext('2d'), viewport }).promise;
  }
}


function scrollToPage(displayZone, pageNum) {
  currentPage = pageNum;
  displayZone.querySelector('[data-element="current-page"]').textContent = pageNum;
  const viewer = displayZone.querySelector('[data-element="viewer"]');
  const target = displayZone.querySelector(`#page-wrapper-${pageNum}`);

  // if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  if (target && viewer) {
    // Calcul manuel de la position, sans scrollIntoView
    const offset = target.offsetTop - viewer.offsetTop;
    viewer.scrollTo({
      top: offset,
      behavior: 'smooth'
    });
  }

}

function changePage(e, delta) {
  const displayZone =  e.target.closest('[data-block-type]')
  const newPage = Math.min(Math.max(currentPage + delta, 1), pdfDoc.numPages);
  scrollToPage(displayZone, newPage);
}

// Mise à jour du numéro de page au scroll
function scrollPage(displayZone) {
  const viewer = displayZone.querySelector('[data-element="viewer"]');
  viewer?.addEventListener('scroll', function () {
    for (let i = 1; i <= (pdfDoc?.numPages || 0); i++) {
      const el = document.querySelector(`#page-wrapper-${i}`);
      if (!el) continue;
      const rect = el.getBoundingClientRect();
      const viewerRect = viewer.getBoundingClientRect();
      if (rect.top >= viewerRect.top - 50) {
        currentPage = i;
        displayZone.querySelector('[data-element="current-page"]').textContent = i;
        break;
      }
    }
  });
}


function closePdf() {
  document.querySelectorAll('[data-block-type="PDF"]').forEach(displayZone => {
    displayZone.querySelector('[data-element="headline"]').classList.add("hidden");
    displayZone.querySelector('[data-element="container"]').classList.add("hidden");
    displayZone.querySelector('[data-element="viewer"]').innerHTML = '';
    pdfDoc = null;
    document.querySelectorAll('.headline-title').forEach(d => d.classList.remove('bg-focuscolor-line'));
  })
}

window.addEventListener('resize', async () => {
  if (!pdfDoc) return;
  await renderAllPages();
  scrollToPage(currentPage);
});
