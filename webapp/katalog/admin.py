from django.contrib import admin

from .models import FavoritePost, Post


# Rejestracja modelu `Post` umożliwia zarządzanie katalogiem w panelu admina.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # To są kolumny widoczne na liście wpisów w panelu administracyjnym.
    list_display = ("title", "category", "tagi", "podtag_anime", "okazja", "liczba_osob", "author", "date")
    # Filtry pomagają szybko zawęzić wyniki po cechach wpisu.
    list_filter = ("category", "tagi", "podtag_anime", "okazja", "liczba_osob", "cena", "date")
    # Wyszukiwanie działa po tytule, opisie i nazwie autora.
    search_fields = ("title", "body", "author__username")


# Ten model pokazuje w panelu admina, kto polubił który wpis.
@admin.register(FavoritePost)
class FavoritePostAdmin(admin.ModelAdmin):
    # Podgląd ulubionych pokazuje użytkownika, wpis i datę dodania.
    list_display = ("user", "post", "created_at")
    # Wyszukiwanie ułatwia sprawdzenie polubień po użytkowniku i tytule wpisu.
    search_fields = ("user__username", "post__title")
