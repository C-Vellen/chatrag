from django.conf import settings

"""si l'app special est présente : réalise les imports"""

has_special = settings.HAS_SPECIAL_APP

if has_special:
    from special.service import add_documents_from_api
    
else:
    def add_documents_from_api(*args, **kwargs):
        return None 