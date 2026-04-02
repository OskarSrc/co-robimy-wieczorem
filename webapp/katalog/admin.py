from django.contrib import admin

from .models import FavoritePost, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "tagi", "podtag_anime", "okazja", "liczba_osob", "author", "date")
    list_filter = ("category", "tagi", "podtag_anime", "okazja", "liczba_osob", "cena", "date")
    search_fields = ("title", "body", "author__username")


@admin.register(FavoritePost)
class FavoritePostAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    search_fields = ("user__username", "post__title")
