import os
import re
import requests
from pathlib import Path
from urllib.parse import urlparse
from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp


def parse_uri(uri: str) -> dict:
    """
    Analyse une URI et retourne son type avec le fichier associé si applicable.

    Returns:
        {"type": "path", "path": str}
        {"type": "filepath", "path": str, "file": InMemoryUploadedFile}
        {"type": "fileurl","path": str,  "file": SimpleUploadedFile}
        {"type": "error", "reason": str}
    """

    # URI de type répertoire : se termine par "/"
    if uri.endswith("/"):
        if os.path.isdir(uri):
            return {"type": "path", "path": uri}
        else:
            return {"type": "error", "reason": f"Directory not found: {uri}"}

    # URI de type URL distante (http/https)
    parsed = urlparse(uri)
    if parsed.scheme in ("http", "https"):
        try:
            response = requests.get(uri, timeout=10, stream=True)
            response.raise_for_status()

            filename = os.path.basename(parsed.path) or "downloaded_file"
            content_type = response.headers.get("Content-Type", "application/octet-stream").split(";")[0].strip()
            content = response.content

            file = SimpleUploadedFile(
                name=filename,
                content=content,
                content_type=content_type,
            )
            return {"type": "fileurl", "path": uri, "file": file}

        except requests.RequestException as e:
            return {"type": "error", "reason": f"Failed to fetch URL: {e}"}

    # URI de type chemin local vers un fichier
    if os.path.isfile(uri):
        filename = os.path.basename(uri)
        content_type = _guess_content_type(filename)

        with open(uri, "rb") as f:
            content = f.read()

        file = InMemoryUploadedFile(
            file=__import__("io").BytesIO(content),
            field_name=None,
            name=filename,
            content_type=content_type,
            size=len(content),
            charset=None,
        )
        return {"type": "filepath", "path": uri, "file": file}

    # Rien trouvé
    return {"type": "error", "reason": f"No file or directory found for URI: {uri}"}


def iter_uri(uri: str):
    """ Itérateur qui retourne tous les fichiers se trouvant dans un dossier, de manière récursive
    Args:
        uri (str): l'uri d'un dossier (ex: documents/data/mesfichiers/)
    Yields:
        _le dictionnaire {"type":"filepath", "file":file} de tous les fichiers qui se trouvent dans le dossier ou ses sous-dossiers
    """
    for path in Path(uri).rglob("*"): 
        if path.is_file():
            result = parse_uri(str(path))
            yield result    
        

def _guess_content_type(filename: str) -> str:
    """Devine le content-type à partir de l'extension."""
    import mimetypes
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"


# -----------FIN REFACTORING ----------------------------------------


def format_time(seconds):
    """Transforme des secondes (ex: 75.5) en chaîne lisible (ex: '01:15')"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def extract_video_id(url):
    """Extrait l'identifiant unique de la vidéo YouTube."""
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

import yt_dlp

def get_video_info(url:str) -> dict :
    """
    Récupère le titre et la durée d'une vidéo YouTube 
    Retourne un dictionnaire {"titre": ..., "duration": ...}
    """
    ydl_opts = {
        "quiet": True,          # N'affiche rien dans la console Django
        "skip_download": True,  # Sécurité : ne télécharge pas le fichier vidéo
        "extract_flat": True,   # Extraction rapide et superficielle des métadonnées
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            
            return {
                "title": info.get("title", "Titre inconnu"),
                "duration": info.get("duration", 0) # durée en format secondes
            }
        except Exception:
            # En cas d'erreur (URL invalide, vidéo privée, etc.)
            return {
                "title": "Titre inconnu (Erreur d'extraction)",
                "duration": 0
            }


def get_youtube_script_with_timestamp(video_url: str) -> dict:
    """ 
    Effectue la transcription d'une video youtube avac l'API youtube_transcript_api
    Args:
        video_url (str): url d'une video youtube
   
    Raises:
        ValueError:     L'URL de la vidéo YouTube est invalide.
        RuntimeError:   Impossible de récupérer les sous-titres
    Returns:
        dict: { "video_id" (str):   id de la video
                "titre" (str):      titre de la video,
                "content" (str):    transcrption de la video
                "timestamp (dict):  dictionnaire horodatage {index_caractère : start_time} 
    """
    
    
    # Récupération video_id
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("L'URL de la vidéo YouTube est invalide.")

    # Récupération du titre et de la durée   
    video_info = get_video_info(video_url)
    title = video_info["title"]
    duration = video_info["duration"]
    

    # Récupération des sous-titres
    try:
        # raw_transcript = YouTubeTranscriptApi.get_transcript(
        #     video_id, languages=["fr", "en"]
        # )
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id, languages=["fr", "en"])
        raw_transcript = fetched_transcript.to_raw_data()
        
    except Exception as e:
        raise RuntimeError(f"Impossible de récupérer les sous-titres : {str(e)}")

    # Construction du contenu et de la table de correspondance horodatage
    full_content = []
    timestamp = {}
    current_char_index = 0 # initialisation de l'index au 1er caractère

    for item in raw_transcript:
        text_segment = item["text"]
        # On arrondit le temps en secondes (ex: 3.45 -> 3) selon votre besoin
        start_time = int(round(item["start"])) # arrondi à la seconde

        # On enregistre l'index de départ de ce bloc de texte
        timestamp[current_char_index] = start_time

        # On ajoute le texte
        full_content.append(text_segment)

        # Mise à jour de l'index en comptant le texte + 1 pour l'espace de séparation
        current_char_index += len(text_segment) + 1

    # On fusionne tous les morceaux avec un espace
    full_content = " ".join(full_content)

    return {"titre": title, "content": full_content, "timestamp": timestamp, "video_id": video_id, "duration": duration}


def is_youtube_url(url: str) -> bool:
    """
    Vérifie si une chaîne est une URL YouTube valide.
    
    Formats supportés :
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://youtube.com/shorts/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - Avec ou sans https/http, www, paramètres supplémentaires (&t=30s, &list=..., etc.)
    """
    if not isinstance(url, str) or not url.strip():
        return False

    pattern = re.compile(
        r'^(https?://)?'                             # http:// ou https:// (optionnel)
        r'(www\.|m\.)?'                              # www. ou m. (optionnel)
        r'(youtube\.com|youtu\.be)'                  # domaine principal
        r'('
            r'/watch\?([^#]*&)?v=[A-Za-z0-9_-]{11}' # /watch?v=VIDEO_ID
            r'|/shorts/[A-Za-z0-9_-]{11}'            # /shorts/VIDEO_ID
            r'|/embed/[A-Za-z0-9_-]{11}'             # /embed/VIDEO_ID
            r'|/v/[A-Za-z0-9_-]{11}'                 # /v/VIDEO_ID (ancien format)
            r'|/[A-Za-z0-9_-]{11}'                   # youtu.be/VIDEO_ID
        r')'
        r'([?&][^#]*)?'                              # paramètres supplémentaires (&t=, &list=…)
        r'(#.*)?$',                                  # ancre (optionnelle)
        re.IGNORECASE
    )
    return bool(pattern.match(url.strip()))


def extract_title(doc: str) -> list:
    """extrait des documents le nom du fichier du chemin, sans l'extension"""        
    filename = doc.split("/")[-1]
    return filename.split(".")[0]
    
    
def get_closest_smaller_index(n: int, liste: list[str]) -> int:
    """Exemple : 
        n= 8
        liste = [0, 5, 12, 20]
        retourne 5
    Args:
        n (int): integer
        liste (list[int]): list of str
    Returns:
        int:    if n >= liste[0] return closest smaller item of the list
                if n < liste[0] return 0
    """
    valid_values = [int(x) for x in liste if int(x) <= n]
    if not valid_values:
        return 0
    return max(valid_values)


def get_closest_bigger_index(n: int, liste: list[str]) -> int | None:
    """Exemple : 
        n= 8
        liste = [0, 5, 12, 20]
        retourne 12
    Args:
        n (int): integer
        liste (list[int]): list of str
    Returns:
        int:    if n <= liste[-1] return closest bigger item of the list
                if n > liste[-1] return None
    """
    valid_values = [int(x) for x in liste if int(x) > n]
    if not valid_values:
        return None
    return min(valid_values)