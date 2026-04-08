from django.apps import AppConfig


class PostsConfig(AppConfig):
    # BigAutoField oznacza duży automatyczny klucz główny dla nowych modeli.
    default_auto_field = 'django.db.models.BigAutoField'
    # To jest techniczna nazwa katalogu aplikacji w projekcie.
    name = 'katalog'
    # `label` ustawia krótszą nazwę aplikacji używaną wewnątrz Django.
    label = 'posts'
