import re
from simple_yt_api import YouTubeAPI




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
    