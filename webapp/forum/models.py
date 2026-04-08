from django.contrib.auth.models import User
from django.db import models

from katalog.models import Post


# Model przechowuje pojedynczy temat forum powiązany z wpisem z katalogu.
class ForumPost(models.Model):
    # Każdy temat jest przypisany do konkretnej pozycji z katalogu.
    catalog_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="forum_posts")
    # To jest krótki tytuł tematu widoczny na liście i na stronie szczegółów.
    subject = models.CharField(max_length=120)
    # Tutaj zapisuje się główna treść posta.
    body = models.TextField(verbose_name="Opis")
    # Autor tematu to zalogowany użytkownik Django.
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="forum_posts")
    # Data dodania ustawia się automatycznie przy tworzeniu rekordu.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Najnowsze tematy mają pojawiać się na początku forum.
        ordering = ["-created_at"]

    def __str__(self):
        # Czytelny podpis obiektu przydaje się w panelu admina i debugowaniu.
        return f"{self.subject} ({self.catalog_post.title})"
