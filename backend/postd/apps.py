from django.apps import AppConfig


class PostdConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'postd'

def ready(self):
    import postd.signals
