// ---------------------------------------------------------
// POPUP DE CONFIRMATION DU BOUTON DE DECONNEXION
// ---------------------------------------------------------


import {displayAlertBox} from './alertbox.js'
document.querySelector("#deconnect-button").addEventListener('click', (e) => displayAlertBox("alert-deconnect"))
