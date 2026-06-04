// ---------------------------------------------------------
// POPUP DE CONFIRMATION DU SUPPRESSION D'UN DOCUMENT
// ---------------------------------------------------------



const alertBox = document.getElementById("alert-delete-doc")
const backButton = alertBox.querySelector("#back-button")

    
function hideAlertBox(e) {
    // masque la boite de confirmation après suppression ou annulation de suppression d'un nouveau contenu
    const shadowMask = document.getElementById("shadow-mask")

    alertBox.classList.add("hidden")
    shadowMask.classList.add("hidden")
}

function deleteDoc(button) {
    const alertBox = document.getElementById("alert-delete-doc")
    const backButton = alertBox.querySelector("#back-button")
    const docId = button.getAttribute('data-id')
    const docTitre = button.getAttribute('data-titre')
    const shortTitre = docTitre.length > 60 ? docTitre.slice(0, 60) + "..." : docTitre;
    const shadowMask = document.getElementById("shadow-mask")
    alertBox.querySelector("a").href = `/ingest/remove_document/${docId}`
    alertBox.querySelector("p").textContent = `Voulez-vous vraiment supprimer le document "${shortTitre}" ?`
    alertBox.classList.remove("hidden")
    shadowMask.classList.remove("hidden")
    backButton.addEventListener('click', hideAlertBox)
} 
    
