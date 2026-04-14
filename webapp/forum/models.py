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


class ForumReply(models.Model):
    # Odpowiedź jest przypisana do konkretnego posta forum
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='replies')
    # Treść odpowiedzi
    body = models.TextField()
    # Autor odpowiedzi
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_replies')
    # Data dodania
    created_at = models.DateTimeField(auto_now_add=True)
    # Data ostatniej edycji
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Odpowiedź {self.author.username} do {self.post.subject}"
