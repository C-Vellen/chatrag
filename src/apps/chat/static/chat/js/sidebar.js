document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const btnOpen = document.getElementById('btn-open');
    const btnClose = document.getElementById('btn-close');

    // Sécurité au cas où les éléments ne sont pas dans la page
    if (!sidebar || !btnOpen || !btnClose) return;

    // Fonction pour OUVRIR la sidebar
    function openSidebar() {
        // On retire les largeurs nulles
        sidebar.classList.remove('w-0', 'lg:w-0');
        // On applique la largeur de 24rem (w-96)
        sidebar.classList.add('w-96', 'lg:w-96');
        btnOpen.classList.add("hidden")
    }

    // Fonction pour FERMER la sidebar
    function closeSidebar() {
        // On retire les grandes largeurs
        sidebar.classList.remove('w-96', 'lg:w-96');
        // On remet la largeur à zéro
        sidebar.classList.add('w-0', 'lg:w-0');
        btnOpen.classList.remove("hidden")
    }

    // Événements de clic
    btnOpen.addEventListener('click', openSidebar);
    btnClose.addEventListener('click', closeSidebar);

    // OPTIONNEL & INTELLIGENT : Déterminer l'état initial selon la taille de l'écran au chargement
    // Version large (>= 1024px, le standard 'lg' de Tailwind) -> Ouvert par défaut
    // Version étroite (< 1024px) -> Fermé par défaut
    if (window.innerWidth >= 1024) {
        openSidebar();
    } else {
        closeSidebar();
    }
});