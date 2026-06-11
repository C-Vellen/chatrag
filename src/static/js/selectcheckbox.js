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

    // --- FONCTIONNALITE 3 : AFFICHER / MASQUER LES DOCUMENTS
    const filterButtons = document.querySelectorAll('.display-doc');

    filterButtons.forEach(button => {
        button.addEventListener('click', function () {
            // 1. On récupère le statut cible (ex: NEW, REG, ERR)
            const statusTarget = this.getAttribute('data-status');
            
            // 2. On cible tous les <li> qui ont la classe correspondante
            // Exemple : .status-NEW, .status-REG, .status-ERR
            const matchingDocs = document.querySelectorAll(`.status-${statusTarget}`);

            // 3. On vérifie si les documents sont actuellement visibles ou masqués
            // On se base sur le premier élément trouvé pour décider de l'action
            let isHidden = false;
            if (matchingDocs.length > 0) {
                isHidden = matchingDocs[0].style.display === 'none';
            }

            // 4. On effectue le TOGGLE
            if (isHidden) {
                // S'ils étaient masqués, on les réaffiche
                matchingDocs.forEach(doc => doc.style.display = '');
                // On remet le bouton à une opacité normale
                this.style.opacity = '1';
                this.style.textDecoration = 'none';
            } else {
                // S'ils étaient visibles, on les masque
                matchingDocs.forEach(doc => doc.style.display = 'none');
                // On grise visuellement le bouton pour indiquer que le statut est masqué
                this.style.opacity = '0.5';
                this.style.textDecoration = 'line-through';
            }
        });
    });
});