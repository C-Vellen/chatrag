from simple_yt_api import YouTubeAPI


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
    


def extract_title(docs: list) -> list:
    """extrait des documents le nom du fichier du chemin, sans l'extension"""
    for doc in docs:
        filename = doc["source"].rsplit("/", 1)[-1]
        doc.update({"title":filename.rsplit(".", 1)[0] })
    return docs  
    