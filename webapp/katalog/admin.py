from django.contrib import admin

from .models import CatalogTag, FavoritePost, Post


@admin.register(CatalogTag)
class CatalogTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "scope", "sort_order")
    list_filter = ("scope",)
    search_fields = ("name", "slug")
    ordering = ("scope", "sort_order", "name")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "subcategory", "tag_list", "author", "date")
    list_filter = ("category", "subcategory", "date", "tags")
    search_fields = ("title", "body", "pick_reason", "author__username", "tags__name")
    filter_horizontal = ("tags",)

    def tag_list(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all()[:3])

    tag_list.short_description = "Tagi"


@admin.register(FavoritePost)
class FavoritePostAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    search_fields = ("user__username", "post__title")
