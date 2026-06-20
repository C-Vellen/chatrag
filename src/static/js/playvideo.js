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


function truncate(text, maxLength = 20) {
    if (!text) return "";
    return text.length > maxLength
        ? text.slice(0, maxLength) + "..."
        : text;
}


function selectVideo(btn, displayZone) {
  closePlayer();
  closePdf();
  closeTxt();
  closeChunksList();
  btn.closest('.headline-title').classList.add('bg-focuscolor-line');
  currentVideo = {
    msg: btn.dataset.msg,
    id: btn.dataset.videoId,
    start: parseInt(btn.dataset.starttime),
    end: parseInt(btn.dataset.endtime),
    titre: btn.dataset.titre,
    duration: parseInt(btn.dataset.duration),
  };
  

  displayZone.querySelector('[data-element="player-iframe"]').classList.add('hidden');
  displayZone.querySelector('[data-element="thumbnail-frame"]').classList.remove('hidden');
  const img = displayZone.querySelector('[data-element="thumbnail"]');
  img.src = `https://img.youtube.com/vi/${currentVideo.id}/maxresdefault.jpg`;
  img.onerror = function() {
    this.src = `https://img.youtube.com/vi/${currentVideo.id}/hqdefault.jpg`;
  };
  // window.scrollTo({top: 0, behavior: "smooth"});
  displayZone.querySelector('[data-element="headline"]').classList.remove('hidden');
  displayZone.querySelector('[data-element="headline"]').classList.add('flex');
  displayZone.querySelector('[data-element="titre"]').textContent = truncate(currentVideo.titre, 60);
  if (currentVideo.end) {
    displayZone.querySelector('[data-element="timestamp"]').textContent = `${formatTime(currentVideo.start)} → ${formatTime(currentVideo.end)}`;
  } else if (currentVideo.duration) {
    displayZone.querySelector('[data-element="timestamp"]').textContent = `durée: ${formatTime(currentVideo.duration)}`; 
  }
}


function playVideo(e) {
  const displayZone =  e.target.closest('[data-block-type]')
  displayZone.querySelector('[data-element="thumbnail-frame"]').classList.add('hidden');
  displayZone.querySelector('[data-element="player-iframe"]').classList.remove('hidden');
  // Détruire le player précédent si existant
  if (ytPlayer) {
    ytPlayer.destroy();
    ytPlayer = null;
  }
  // Recréer le div cible (destroy() le supprime du DOM)
  const container = displayZone.querySelector('[data-element="player-iframe"]');
  let target = displayZone.querySelector('[data-element="yt-player"]');
  if (!target) {
    target = document.createElement('div');
    target.setAttribute('data-element', 'yt-player');
    target.id = `yt-player-${currentVideo.msg}`
    target.className = 'w-full h-full';
    container.insertBefore(target, container.firstChild);
  } else {
    target.id = `yt-player-${currentVideo.msg}`
  }
  const start = currentVideo.start;
  const end = currentVideo.end;
  
  ytPlayer = new YT.Player(`yt-player-${currentVideo.msg}`, {
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
        console.log("------- e.target: --------")
        console.log(target)
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


function stopAndReset(displayZone) {
  clearTimeout(endTimer);
  document.querySelectorAll('.headline-title').forEach(d => d.classList.remove('bg-focuscolor-line'));
  displayZone.querySelector('[data-element="titre"]').textContent = "";
  displayZone.querySelector('[data-element="timestamp"]').textContent = "";
  if (ytPlayer) {
    try { ytPlayer.stopVideo(); } catch(e) {}
  }
}


function closePlayer() {
  document.querySelectorAll('[data-block-type="YT"]').forEach(displayZone => {
    stopAndReset(displayZone);
    if (ytPlayer) {
      ytPlayer.destroy();
      ytPlayer = null;
    }
    // Recréer le div cible pour la prochaine utilisation
    const container = displayZone.querySelector('[data-element="player-iframe"]');
    let target = displayZone.querySelector('[data-element="yt-player"]');
    if (!target) {
      target = document.createElement('div');
      target.setAttribute('data-element', 'yt-player');
      target.className = 'w-full h-full';
      container.insertBefore(target, container.firstChild);
    }
    displayZone.querySelector('[data-element="headline"]').classList.add('hidden');
    displayZone.querySelector('[data-element="player-iframe"]').classList.add('hidden');
    displayZone.querySelector('[data-element="thumbnail-frame"]').classList.add('hidden');
    currentVideo = null;
  }) 
}