from django.contrib import admin

from .models import ForumPost


# Rejestracja modelu sprawia, że posty forum są widoczne w panelu admina.
@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    # Kolumny wyświetlane na liście rekordów w panelu administracyjnym.
    list_display = ("subject", "catalog_post", "author", "created_at")
    # Wyszukiwanie działa po temacie, treści, tytule z katalogu i nazwie autora.
    search_fields = ("subject", "body", "catalog_post__title", "author__username")
    # Filtry ułatwiają zawężanie wyników po kategorii i dacie.
    list_filter = ("catalog_post__category", "created_at")
