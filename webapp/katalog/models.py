from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
# Create your models here.


class Post(models.Model):
    CATEGORY_CHOICES = [
        ("film", "Film"),
        ("serial", "Serial"),
        ("gra", "Gra"),
        ("aktywnosci", "Aktywności"),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="film")
    title = models.CharField(max_length=75)
    body = models.TextField(verbose_name="Krótki opis")
    slug = models.SlugField(unique=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    banner = models.ImageField(default='fallback.png', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "katalog"
            slug = base_slug
            counter = 1
            while Post.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
