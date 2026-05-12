// ---------------------------------------------------------
// GESTION DES POPUPS DE CONFIRMATION DES BOUTONS D'ACTION
// ---------------------------------------------------------

// ! les fonctions displayAlertBox et hideAlertBox devraient être exportées vers user/tuto_admin.js et assets/set_form.js !

export function displayAlertBox(alertbox) {
    // affiche une boite de confirmation avant de supprimer un nouveau contenu
    const alertBox = document.querySelector("#"+alertbox)
    const shadowMask = document.getElementById("shadow-mask")
    const backButton = alertBox.querySelector("#back-button")
    
    alertBox.classList.remove("hidden")
    shadowMask.classList.remove("hidden")
    backButton.addEventListener('click', hideAlertBox)
  }
  
export function hideAlertBox(e) {
    // masque la boite de confirmation après suppression ou annulation de suppression d'un nouveau contenu
    const alertBox = e.target.closest(".alert-box")
    const shadowMask = document.getElementById("shadow-mask")
    alertBox.classList.add("hidden")
    shadowMask.classList.add("hidden")
  }
    
// document.querySelector("#deconnect-button").addEventListener('click', (e) => displayAlertBox("alert-deconnect"))

