from django.contrib import admin
from .models import Post

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'date')
    list_filter = ('category', 'date')
    search_fields = ('title', 'body', 'author__username')
