from django.apps import AppConfig


# To podstawowa konfiguracja aplikacji `main` widzianej przez Django.
class MainConfig(AppConfig):
    # `BigAutoField` daje duże automatyczne ID dla nowych modeli.
    default_auto_field = 'django.db.models.BigAutoField'
    # Ta nazwa musi zgadzać się z nazwą folderu aplikacji.
    name = 'main'
