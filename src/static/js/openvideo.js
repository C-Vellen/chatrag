
function extractYoutubeId(url) {
    // Gère les formats : youtube.com/watch?v=ID et youtu.be/ID
    const match = url.match(/(?:v=|youtu\.be\/)([^&?/]+)/);
    return match ? match[1] : null;
}

function openVideoModal(url, startTime, endTime) {
    const videoId = extractYoutubeId(url);
    if (!videoId) return;

    console.log(">>> openVideoMo")

    // Paramètres YouTube : start, end, autoplay
    const embedUrl = `https://www.youtube.com/embed/${videoId}`
                   + `?start=${startTime}&end=${endTime}&autoplay=1`;

    document.getElementById("video-iframe").src = embedUrl;

    const modal = document.getElementById("video-modal");
    modal.style.display = "flex";
}

function closeVideoModal() {
    // Stoppe la vidéo en vidant le src
    document.getElementBmonnaieyId("video-iframe").src = "";
    document.getElementById("video-modal").style.display = "none";
}

// Fermer en cliquant en dehors de la fenêtre
document.getElementById("video-modal").addEventListener("click", function(e) {
    if (e.target === this) closeVideoModal();
});