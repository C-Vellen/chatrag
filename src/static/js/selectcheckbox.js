// Gestion de la page d'affichage de la waitinglist:
// - coche / décoche des documents à ingérer
// - afficher / masquer (toggle) les documents ingérés / nouveaux / introuvables


document.addEventListener('DOMContentLoaded', function () {
    const checkAll = document.getElementById('check-all');
    const checkboxes = Array.from(document.querySelectorAll('.doc-checkbox'));
    let lastChecked = null; // Garde en mémoire la dernière case cliquée

    // --- FONCTIONNALITÉ 1 : TOUT COCHER / TOUT DÉCOCHER ---
    if (checkAll) {
        checkAll.addEventListener('click', function () {
            checkboxes.forEach(cb => {
                cb.checked = checkAll.checked;
            });
        });
    }

    // --- FONCTIONNALITÉ 2 : SÉLECTION MULTIPLE AVEC SHIFT ---
    checkboxes.forEach((checkbox, index) => {
        checkbox.addEventListener('click', function (e) {
            // On vérifie si la touche SHIFT est enfoncée ET s'il y a un clic précédent
            if (e.shiftKey && lastChecked !== null) {
                const currentIndex = checkboxes.indexOf(this);
                const lastIndex = checkboxes.indexOf(lastChecked);

                // On détermine le début et la fin de la zone (gère la sélection vers le haut ou le bas)
                const start = Math.min(lastIndex, currentIndex);
                const end = Math.max(lastIndex, currentIndex);

                // On applique l'état de la case actuelle à toutes les cases de l'intervalle
                for (let i = start; i <= end; i++) {
                    checkboxes[i].checked = this.checked;
                }
            }

            // On sauvegarde cette case comme étant la dernière cliquée pour le prochain Shift+clic
            lastChecked = this;
        });
    });

 
});