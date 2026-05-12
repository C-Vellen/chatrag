import os
from .base import BASE_DIR, INSTALLED_APPS, MIDDLEWARE


SECRET_KEY = "django-insecure-<50-char-password>"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:8000", "http://localhost:8000"]

INSTALLED_APPS += [
    "debug_toolbar",
    "django_browser_reload",
    ]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    ] 

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# désactivation du cache en dev pour que les modifications sur les fichiers statiques soient prises en compte:
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"