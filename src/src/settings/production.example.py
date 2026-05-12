import os
from .base import BASE_DIR


SECRET_KEY = "django-insecure-<50-char-password>"
DEBUG = False
ALLOWED_HOSTS =  ['mondomaine.fr', 'www.mondomaine.fr']
CSRF_TRUSTED_ORIGINS = ["https://mondomaine.fr", "https://www.mondomaine.fr"]

STATIC_ROOT = "/app/src/staticfiles"
MEDIA_ROOT = "/app/src/media"
 