from .base import *
# from ..celery import app as celery_app
# __all__ = ('celery_app',)

try:
    from .develop import *
except ModuleNotFoundError:
    pass

try:
    from .production import *
except ModuleNotFoundError:
    pass