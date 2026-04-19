from django.db import models

from katalog.models import Post


class Club(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    color = models.CharField(max_length=7, default="#6366f1")
    icon = models.CharField(max_length=50, default="")
    posts = models.ManyToManyField(Post, blank=True, related_name="clubs")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]