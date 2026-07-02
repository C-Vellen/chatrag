import os
from celery import Celery

# Indique à Celery quel fichier de settings Django utiliser
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

# Crée l'application Celery, nommée comme le projet
app = Celery('chatrag')

# Charge la configuration depuis Django settings,
# en cherchant les clés qui commencent par "CELERY_"
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvre automatiquement les tâches dans tous les fichiers tasks.py
# de chaque app Django installée
app.autodiscover_tasks()