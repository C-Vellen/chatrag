pdfjsLib.GlobalWorkerOptions.workerSrc = PDF_WORKER_URL;

var pdfDoc = null;
var currentPage = 1;

async function selectPdf(btn) {
  const fileUrl = btn.dataset.file;
  const targetPage = parseInt(btn.dataset.page) || 1;
  const titre = btn.dataset.titre;
  closePlayer()
  closeTxt()
  document.querySelectorAll('.chunk-title').forEach(d => d.classList.remove('bg-blue-100')); 
  btn.closest('.chunk-title').classList.add('bg-blue-100');
 
  document.getElementById('pdf-titre').textContent = titre;

  const titrePagination = document.getElementById('pdf-titre-pagination')
  const viewer = document.getElementById('pdf-viewer')

  titrePagination.classList.remove("hidden");
  titrePagination.classList.add("flex");
  viewer.classList.remove("hidden");
  viewer.classList.add("flex");
  
  pdfDoc = await pdfjsLib.getDocument(fileUrl).promise;
  document.getElementById('pdf-page-total').textContent = pdfDoc.numPages;

  await renderAllPages();
  scrollToPage(targetPage);
  window.scrollTo({top: 0, behavior: "smooth"});
}

async function renderAllPages() {

  const container = document.getElementById('pdf-container');
  const viewer = document.getElementById('pdf-viewer');

  container.innerHTML = '';

  for (let i = 1; i <= pdfDoc.numPages; i++) {
    const page = await pdfDoc.getPage(i);
    const naturalViewport = page.getViewport({ scale: 1 });


    // Calcule le scale pour que la page remplisse exactement la largeur du container
    // (32px = padding p-4 × 2 côtés)
    const availableWidth = container.clientWidth - 32;
    const scale = availableWidth / naturalViewport.width;
    const viewport = page.getViewport({ scale });


    // Après la première page, fixe la hauteur du viewer = hauteur d'une page + header
    if (i === 1) {
      viewer.style.height = `${viewport.height + 32}px`;
    }

    const wrapper = document.createElement('div');
    wrapper.id = `page-wrapper-${i}`;
    wrapper.className = 'w-full';

    const canvas = document.createElement('canvas');
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    canvas.className = 'w-full shadow-md';

    wrapper.appendChild(canvas);
    container.appendChild(wrapper);

    await page.render({ canvasContext: canvas.getContext('2d'), viewport }).promise;
  }
}

  function scrollToPage(pageNum) {
    currentPage = pageNum;
    document.getElementById('pdf-page-current').textContent = pageNum;
    const target = document.getElementById(`page-wrapper-${pageNum}`);
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function changePage(delta) {
    const newPage = Math.min(Math.max(currentPage + delta, 1), pdfDoc.numPages);
    scrollToPage(newPage);
    window.scrollTo({top: 0, behavior: "smooth"});
  }

  // Mise à jour du numéro de page au scroll
  document.getElementById('pdf-container')?.addEventListener('scroll', function () {
    const container = this;
    for (let i = 1; i <= (pdfDoc?.numPages || 0); i++) {
      const el = document.getElementById(`page-wrapper-${i}`);
      if (!el) continue;
      const rect = el.getBoundingClientRect();
      const containerRect = container.getBoundingClientRect();
      if (rect.top >= containerRect.top - 50) {
        currentPage = i;
        document.getElementById('pdf-page-current').textContent = i;
        break;
      }
    }
  });

  function closePdf() {
    document.getElementById('pdf-titre-pagination').classList.add("hidden");
    document.getElementById('pdf-viewer').classList.add("hidden");
    document.getElementById('pdf-container').innerHTML = '';
    pdfDoc = null;
    document.querySelectorAll('.chunk-title').forEach(d => d.classList.remove('bg-blue-100'));

  }

  window.addEventListener('resize', async () => {
  if (!pdfDoc) return;
  await renderAllPages();
  scrollToPage(currentPage);
});
