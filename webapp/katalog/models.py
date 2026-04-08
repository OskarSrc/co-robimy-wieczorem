from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField


# Model `Post` przechowuje pojedynczą propozycję widoczną w katalogu.
class Post(models.Model):
    # Podstawowe kategorie wpisów w katalogu.
    CATEGORY_CHOICES = [
        ("film", "Film"),
        ("serial", "Serial"),
        ("gra", "Gra"),
        ("aktywnosci", "Aktywno\u015bci"),
    ]

    # Proste tagi tematyczne są pogrupowane tak, żeby były czytelne w formularzu.
    TAG_CHOICES = [
        (
            "Filmy/Seriale",
            [
                ("akcja", "Akcja"),
                ("anime", "Anime"),
                ("animacja", "Animacja"),
                ("komedia", "Komedia"),
                ("dramat", "Dramat"),
                ("horror", "Horror"),
                ("sci_fi", "Sci-Fi"),
                ("do_obiadu", "Do obiadu"),
            ],
        ),
        (
            "Gry",
            [
                ("rpg", "RPG"),
                ("fps", "FPS"),
                ("strategia", "Strategia"),
                ("przygodowa", "Przygodowa"),
                ("logiczna", "Logiczna"),
            ],
        ),
        (
            "Aktywno\u015bci",
            [
                ("sport", "Sport"),
                ("jedzenie", "Jedzenie"),
                ("spacer", "Spacer"),
                ("impreza", "Impreza"),
                ("kino", "Kino"),
                ("kultura", "Kultura"),
            ],
        ),
    ]

    # Dodatkowe cechy wpisu pomagają szybciej dopasować propozycję do sytuacji.
    OKAZJA_CHOICES = [
        ("na_randke", "Na randk\u0119"),
        ("ze_znajomymi", "Ze znajomymi"),
        ("solo", "Samemu (Solo)"),
    ]

    LICZBA_OSOB_CHOICES = [
        ("1_osoba", "1 osoba"),
        ("2_osoby", "2 osoby"),
        ("grupa", "Grupa (3+)"),
    ]

    CENA_CHOICES = [
        ("za_darmo", "Za darmo"),
        ("tanio", "Tanio"),
        ("srednio", "\u015arednio"),
        ("drogo", "Drogo"),
    ]

    # Dodatkowy tag jest dostępny tylko wtedy, gdy główny tag to Anime.
    TAGI_ANIME_CHOICES = [
        ("shonen", "Shonen"),
        ("seinen", "Seinen"),
        ("fantasy", "Fantasy"),
    ]

    # To są najważniejsze dane wpisu widoczne od razu na liście i w szczegółach.
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="film",
        verbose_name="Kategoria",
    )
    title = models.CharField(max_length=75, verbose_name="Tytu\u0142")
    body = models.TextField(verbose_name="Kr\u00f3tki opis")

    # Jedno proste pole zamiast relacji ManyToMany jest łatwiejsze do zrozumienia na start.
    tagi = models.CharField(
        max_length=30,
        choices=TAG_CHOICES,
        blank=True,
        default="",
        verbose_name="Tagi",
    )
    # To pole ma sens tylko wtedy, gdy użytkownik wybrał wcześniej tag Anime.
    podtag_anime = models.CharField(
        max_length=30,
        choices=TAGI_ANIME_CHOICES,
        blank=True,
        default="",
        verbose_name="Dodatkowy tag anime",
    )
    okazja = models.CharField(
        max_length=30,
        choices=OKAZJA_CHOICES,
        blank=True,
        default="",
        verbose_name="Okazja",
    )
    liczba_osob = models.CharField(
        max_length=30,
        choices=LICZBA_OSOB_CHOICES,
        blank=True,
        default="",
        verbose_name="Liczba os\u00f3b",
    )
    cena = models.CharField(
        max_length=30,
        choices=CENA_CHOICES,
        blank=True,
        default="",
        verbose_name="Cena",
    )

    # `slug` buduje czytelny adres URL, a `date` zapisuje moment dodania wpisu.
    slug = models.SlugField(unique=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    # Pole Cloudinary przechowuje obrazek okładki wpisu.
    banner = CloudinaryField("image", default="fallback", blank=True)

    # Gdy usuniesz autora, jego wpisy w katalogu też zostaną usunięte.
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
    )

    def __str__(self):
        # Czytelna reprezentacja obiektu przydaje się w panelu admina i debugowaniu.
        return self.title

    def save(self, *args, **kwargs):
        # Slug tworzymy tylko raz, żeby adres wpisu był stabilny.
        if not self.slug:
            base_slug = slugify(self.title) or "katalog"
            slug = base_slug
            counter = 1

            # Pętla pilnuje, żeby slug był unikalny nawet przy takich samych tytułach.
            while Post.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        # Na końcu zapisujemy obiekt standardową metodą modelu Django.
        super().save(*args, **kwargs)


# Ten model przechowuje informację, kto dodał dany wpis do ulubionych.
class FavoritePost(models.Model):
    # Polubienie znika automatycznie razem z użytkownikiem lub wpisem.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_posts")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ta para ma być unikalna, żeby jeden użytkownik nie dodał tego samego wpisu kilka razy.
        unique_together = ("user", "post")
        # Najnowsze polubienia są pokazywane jako pierwsze.
        ordering = ["-created_at"]

    def __str__(self):
        # Taki zapis od razu pokazuje relację użytkownik -> post.
        return f"{self.user.username} -> {self.post.title}"
