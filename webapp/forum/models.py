from django.contrib.auth.models import User
from django.db import models

from katalog.models import Post


class ForumPost(models.Model):
    catalog_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="forum_posts")
    subject = models.CharField(max_length=120)
    body = models.TextField(verbose_name="Opis")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="forum_posts")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} ({self.catalog_post.title})"
