from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from cloudinary.models import CloudinaryField

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
    
    # Pole Cloudinary gotowe do działania
    banner = CloudinaryField('image', default='fallback', blank=True)
    
    # Kaskadowe usuwanie - gdy usuniesz autora, znikną jego posty
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "katalog"
            slug = base_slug
            counter = 1
            # Pętla upewniająca się, że slug jest w 100% unikalny
            while Post.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class FavoritePost(models.Model):
    # Jeśli usuniesz użytkownika lub post, polubienie również automatycznie zniknie (CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_posts")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} -> {self.post.title}"