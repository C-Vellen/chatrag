from django.conf import settings

"""si l'app special est présente : réalise les imports"""

has_special = settings.HAS_SPECIAL_APP

if has_special:
    from special.service import ingest_waitingList
    from special.service import get_documents_from_api
    
else:
    def ingest_waitingList(*args, **kwargs):
        return None 
    def get_documents_from_api(*args, **kwargs):
        return None