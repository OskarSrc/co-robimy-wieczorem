from django.apps import AppConfig


class ForumConfig(AppConfig):
    # BigAutoField oznacza duży automatyczny klucz główny dla nowych modeli.
    default_auto_field = 'django.db.models.BigAutoField'
    # Ta nazwa musi zgadzać się z nazwą aplikacji w projekcie Django.
    name = 'forum'
