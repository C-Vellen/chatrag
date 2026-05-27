import re
import bisect
from simple_yt_api import YouTubeAPI
from django.http import JsonResponse
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

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


def get_video_title(url):
    """Récupère le titre de la vidéo de manière légère avec yt-dlp."""
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info.get("title", "Titre inconnu")
        except Exception:
            return "Titre inconnu (Erreur d'extraction)"


def get_youtube_script_with_mapping(video_url: str) -> dict:
    """ 
    Effectue la transcription d'une video youtube avac l'API youtube_transcript_api
    Args:
        video_url (str): url d'une video youtube
   
    Raises:
        ValueError: L'URL de la vidéo YouTube est invalide.
        RuntimeError: Impossible de récupérer les sous-titres
    Returns:
        dict: { "titre" (str): titre de la video,
                "content" (str): transcrption de la video
                "timestamp (dict): dictionnaire horodatage {index_caractère : start_time} 
    """
    
    
    # Récupération video_id
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("L'URL de la vidéo YouTube est invalide.")

    # Récupération du titre
    title = get_video_title(video_url)

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

    return {"titre": title, "content": full_content, "timestamp": timestamp}

 

# ----------------------------------------------------------------------------------------


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


def video_transcript(url: str) -> dict:
    """Transcription de la video à partir de l'url de Youtube
        Retourne un dictionnaire avec les clés :
      - "titre"   : titre du document (utilisé dans les métadonnées)
      - "content" : contenu texte du document
      """
    
    yt = YouTubeAPI()
    try:
        data, transcript = yt.get_video_data_and_transcript(
            url=url,
            language_code="fr",
            as_dict=False,
        )
        return {
            "titre":data["title"],
            "content":transcript
        }
        
    except YouTubeAPI:
        print("Erreur transcription !")



def video_transcript_in_file(url: str) -> str:
    """Transcription de la video
        entrée : url de la video Youtube
        sortie : chemin du fichier de la transcription"""
    yt = YouTubeAPI()

    try:
        data, transcript = yt.get_video_data_and_transcript(
            url=url,
            language_code="fr",
            as_dict=False,
        )
        # transcript2 = yt.get_transcript(
        #     url=url, language_code="fr", as_dict=True
        # )
        video_has_transcript = True
        video_title = data["title"]
        short_description = data["short_description"]
        thumbnail_url = data["img_url"]
        
        source = f"src/documents/{video_title}.txt"
        print("\n📝 Transcription terminée." )
        
        with open(source, mode='w', encoding='utf-8') as file:
            file.write(transcript)
        print("💾 Transcription enregistrée dans documents/")
        return source
    except YouTubeAPI:
        print("Erreur transcription !")
    

def extract_title(doc: str) -> list:
    """extrait des documents le nom du fichier du chemin, sans l'extension"""        
    filename = doc.split("/")[-1]
    return filename.split(".")[0]
    

def extract_title_list(docs: list) -> list:
    """extrait des documents le nom du fichier du chemin, sans l'extension"""
    for doc in docs:
        filename = doc["source"].rsplit("/", 1)[-1]
        doc.update({"title":filename.rsplit(".", 1)[0] })
    return docs  
    
    
    
def get_closest_smaller_index(n: int, liste: list[str]) -> int:
    """_summary_

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
    """_summary_

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