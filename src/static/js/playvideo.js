// YouTube IFrame API 

var currentVideo = null;
let ytPlayer = null;
let endTimer = null;

// Appelé automatiquement par l'API YouTube quand elle est prête
function onYouTubeIframeAPIReady() {}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0');
  const s = (seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

function selectVideo(btn) {
  closePdf();
  closeTxt();
  stopAndReset();
  btn.closest('.headline-title').classList.add('bg-header', 'text-white');
  currentVideo = {
    id: btn.dataset.videoId,
    start: parseInt(btn.dataset.start),
    end: parseInt(btn.dataset.end),
    titre: btn.dataset.titre,
  };
  document.getElementById('player-iframe').classList.add('hidden');
  document.getElementById('player-thumb').classList.remove('hidden');
  const img = document.getElementById('thumb-img');
  img.src = `https://img.youtube.com/vi/${currentVideo.id}/maxresdefault.jpg`;
  img.onerror = function() {
    this.src = `https://img.youtube.com/vi/${currentVideo.id}/hqdefault.jpg`;
  };
  window.scrollTo({top: 0, behavior: "smooth"});
  document.getElementById('thumb-titre-horodate').classList.remove('hidden');
  document.getElementById('thumb-titre-horodate').classList.add('flex');
  document.getElementById('thumb-titre').textContent = currentVideo.titre;
  if (currentVideo.end) {
    document.getElementById('timestamp').textContent = `${formatTime(currentVideo.start)} → ${formatTime(currentVideo.end)}`;
  }
}

function playVideo() {
  if (!currentVideo) return;
  document.getElementById('player-thumb').classList.add('hidden');
  document.getElementById('player-iframe').classList.remove('hidden');
  // Détruire le player précédent si existant
  if (ytPlayer) {
    ytPlayer.destroy();
    ytPlayer = null;
  }
  // Recréer le div cible (destroy() le supprime du DOM)
  const container = document.getElementById('player-iframe');
  let target = document.getElementById('yt-player');
  if (!target) {
    target = document.createElement('div');
    target.id = 'yt-player';
    target.className = 'w-full h-full';
    container.insertBefore(target, container.firstChild);
  }
  const start = currentVideo.start;
  const end = currentVideo.end;
  ytPlayer = new YT.Player('yt-player', {
    width: '100%',
    height: '100%',
    videoId: currentVideo.id,
    playerVars: {
      autoplay: 1,
      start: start,
      rel: 0,
      modestbranding: 1,
    },
    events: {
      onReady: function(e) {
        e.target.playVideo();
        if (end) {
          scheduleEnd(end - start);
        }
      },
      onStateChange: function(e) {
        // Relance le timer si l'utilisateur repart depuis le début
        if (e.data === YT.PlayerState.PLAYING) {
          clearTimeout(endTimer);
          const remaining = end - Math.floor(e.target.getCurrentTime());
          if (remaining > 0) scheduleEnd(remaining);
        }
      }
    }
  });
}

function scheduleEnd(seconds) {
  clearTimeout(endTimer);
  endTimer = setTimeout(function() {
    if (ytPlayer && ytPlayer.pauseVideo) {
      ytPlayer.pauseVideo();
    }
  }, seconds * 1000);
}

function stopAndReset() {
  clearTimeout(endTimer);
  document.querySelectorAll('.headline-title').forEach(d => d.classList.remove('bg-header', 'text-white'));
  if (ytPlayer) {
    try { ytPlayer.stopVideo(); } catch(e) {}
  }
}


function closePlayer() {
  stopAndReset();
  if (ytPlayer) {
    ytPlayer.destroy();
    ytPlayer = null;
  }
  // Recréer le div cible pour la prochaine utilisation
  const container = document.getElementById('player-iframe');
  let target = document.getElementById('yt-player');
  if (!target) {
    target = document.createElement('div');
    target.id = 'yt-player';
    target.className = 'w-full h-full';
    container.insertBefore(target, container.firstChild);
  }
  document.getElementById('thumb-titre-horodate').classList.add('hidden');
  document.getElementById('player-iframe').classList.add('hidden');
  document.getElementById('player-thumb').classList.add('hidden');
  currentVideo = null;
}