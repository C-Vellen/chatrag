// Actions clic sur un document :
//    -> affichage de la video, pdf ou txt (view-doc)
// ou -> affichage de la liste des chunks (view-chunks)
// ou -> suppression du document (delete-doc)


document.getElementById('list-documents').addEventListener('click', async (e) => {
    const button = e.target.closest('button')
    if (!button) return
    if (button.classList.contains("view-doc")) {
        switch (button.getAttribute('data-source')) {
            case "YT":
                console.log("******** YT")
                selectVideo(button)
                break
            case "PDF":
                selectPdf(button)
                break
            case "TXT":
                selectText(button)
                break
            default:
                return
        }
    } else if (button.classList.contains("view-chunks")) {
        await selectChunksList(button)
    } else if (button.classList.contains("delete-doc")) {
        deleteDoc(button)
        }
    }
)

function hideAlertBox(e) {
    // masque la boite de confirmation après suppression ou annulation de suppression d'un nouveau contenu
    const alertBox = document.getElementById("alert-delete-doc")
    const shadowMask = document.getElementById("shadow-mask")

    alertBox.classList.add("hidden")
    shadowMask.classList.add("hidden")
  }