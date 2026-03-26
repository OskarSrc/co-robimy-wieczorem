from django.contrib import admin

from .models import ForumPost


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ("subject", "catalog_post", "author", "created_at")
    search_fields = ("subject", "body", "catalog_post__title", "author__username")
    list_filter = ("catalog_post__category", "created_at")
