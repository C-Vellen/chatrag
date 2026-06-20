// Actions clic sur un document :
//    -> affichage de la video, pdf ou txt (view-doc)
// ou -> affichage de la liste des chunks (view-chunks)
// ou -> suppression du document (delete-doc)

const clickReceiver = document.querySelector('[data-click-receiver]')
clickReceiver.addEventListener('click', async (e) => {
    const button = e.target.closest('button')

    if (!button) return

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