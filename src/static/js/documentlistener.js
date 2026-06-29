// Actions clic sur un document :
//    -> affichage de la video, pdf ou txt (view-doc)
// ou -> affichage de la liste des chunks (view-chunks)
// ou -> suppression du document (delete-doc)
// ou -> sélection de nouveaux documents pour injection

let lastChecked = null; // Garde en mémoire la dernière case cliquée

const clickReceiver = document.querySelector('[data-click-receiver]')
clickReceiver.addEventListener('click', async (e) => {
    const button = e.target.closest('button')
     if (!button) return

     if (button.type === "submit") {
        return
    };
    
    if (e.target.type !== 'checkbox') {
        e.preventDefault();
    }
   
    const msgId = (button.dataset.msg)? button.dataset.msg : "all"
    const viewer = document.querySelector(`[data-viewer="${msgId}"]`)
    let displayZone = null
    
    if (button.classList.contains("view-doc")) {
        // affichage document dans la displayzone
        switch (button.dataset.source) {
            case "YT":
                displayZone = viewer.querySelector('[data-block-type="YT"]')
                selectVideo(button, displayZone)
                break
            case "PDF":
                displayZone = viewer.querySelector('[data-block-type="PDF"]')
                selectPdf(button, displayZone)
                scrollPage(displayZone)
                break
            case "TXT":
                displayZone = viewer.querySelector('[data-block-type="TXT"]')
                selectText(button, displayZone)
                break
            default:
                return
        }
        if (msgId != "all") {
          // gère le scroll du document dans la page dans le chat
            viewer.classList.remove('grid-rows-[0fr]');
            viewer.classList.add('grid-rows-[1fr]');
            if (button.dataset.source === "YT" ) {
                setTimeout(() => {
                    displayZone.scrollIntoView({                                                             
                        behavior: 'smooth',                                    
                        block: 'end',       // Aligne le BAS du container vidéo avec le BAS de la fenêtre   
                    });
                }, 310); // 310ms pour laisser l'animation CSS se terminer proprement
            } else if (["PDF", "TXT"].includes(button.dataset.source)) {
                setTimeout(() => {
                        const assistantMsg = viewer.closest('.assistant-message');
                        const scrollTarget = assistantMsg || displayZone;
                        scrollTarget.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start',
                    });
                }, 310); 


            }
        }
      
    } else if (button.classList.contains("view-chunks")) {
        // affichage chunks du document dans la displayZone
        await selectChunksList(button, displayZone)

    } else if (button.classList.contains("delete-doc")) {
        // suppression du document
        deleteDoc(button)
    
    } else if (button.hasAttribute('data-status')) {
        // affichage / masquage des documents selon leur status
        const statusTarget = button.dataset.status
        console.log(">>>", statusTarget)
        const matchingDocs = document.querySelectorAll(`.status-${statusTarget}`);
        let isHidden = false;
        if (matchingDocs.length > 0) {
            isHidden = matchingDocs[0].style.display === 'none';
        }
        if (isHidden) {
                // S'ils étaient masqués, on les réaffiche
                matchingDocs.forEach(doc => doc.style.display = '');
                // On remet le bouton à une opacité normale
                button.style.opacity = '1';
                button.style.textDecoration = 'none';
            } else {
                // S'ils étaient visibles, on les masque
                matchingDocs.forEach(doc => doc.style.display = 'none');
                // On grise visuellement le bouton pour indiquer que le statut est masqué
                button.style.opacity = '0.5';
                button.style.textDecoration = 'line-through';
            }

    } else if (button.id === 'check-all') {
        // tout cocher / décocher la liste de nouveaux documents 
        const checkAll = button.querySelector('input');
        // Si on a cliqué sur le bouton autour de l'input, on change son état manuellement :
        if (e.target !== checkAll){
            checkAll.checked = !checkAll.checked
        }
        console.log('>', button.id)
        const checkboxes = document.querySelectorAll('.doc-checkbox input');
        console.log(`> ${checkboxes.length} documents trouvés à modifier.`);
        checkboxes.forEach(cb => {
            cb.checked = checkAll.checked;
        });
  
    } else if (button.classList.contains('doc-checkbox')) {
        // sélection multiple de nouveaux documents avec SHIFT
        const checkboxes = Array.from(document.querySelectorAll('.doc-checkbox input'));
        const clickedCheckbox = button.querySelector("input")
        // Si on a cliqué sur le bouton autour de l'input, on change son état manuellement :
        if (e.target !== clickedCheckbox) {
            clickedCheckbox.checked = !clickedCheckbox.checked;
        }
        if (e.shiftKey && lastChecked !== null) {
            const currentIndex = checkboxes.indexOf(clickedCheckbox);
            const lastIndex = checkboxes.indexOf(lastChecked);

            // On détermine le début et la fin de l'intervalle (sélection vers le haut ou le bas)
            const start = Math.min(lastIndex, currentIndex);
            const end = Math.max(lastIndex, currentIndex);

            // On applique l'état de la case actuelle (cochée ou décochée) à tout l'intervalle
            for (let i = start; i <= end; i++) {
                if ( checkboxes[i]) {
                    checkboxes[i].checked = clickedCheckbox.checked;
                }
            }
        }
        // On sauvegarde cette case pour le prochain Shift+clic
        lastChecked = clickedCheckbox;
    
    
    } else if (button.dataset.action ) {

        switch(button.dataset.action) {
            case "play":
                playVideo(e);
                break;
            case "closeVideo":
                closePlayer();
            case "pageDown":
                changePage(e, -1);
                break;
            case "pageUp":
                changePage(e, +1);
                break;
            case "closePdf":
                closePdf();
        }
    }
})

    

function hideAlertBox(e) {
    // masque la boite de confirmation après suppression ou annulation de suppression d'un nouveau contenu
    const alertBox = document.getElementById("alert-delete-doc")
    const shadowMask = document.getElementById("shadow-mask")

    alertBox.classList.add("hidden")
    shadowMask.classList.add("hidden")
  }