from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class CatalogTag(models.Model):
    # "scope" mówi, do jakiej części formularza należy tag.
    # Dzięki temu mamy jedną tabelę tagów, ale nadal rozróżniamy
    # tagi wspólne od filmowych, serialowych, growych i dla aktywności.
    SCOPE_CHOICES = [
        ("shared", "Wspólne"),
        ("film", "Film"),
        ("serial", "Serial"),
        ("gra", "Gra"),
        ("aktywnosci", "Aktywności"),
    ]

    name = models.CharField(max_length=40)
    slug = models.SlugField(max_length=40, unique=True)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default="shared")
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["scope", "sort_order", "name"]

    def __str__(self):
        return self.name


class Post(models.Model):
    # Jedna konfiguracja dla kategorii ułatwia utrzymanie formularza,
    # tagów i opisów bez rozbijania tych reguł po wielu miejscach.
    CATEGORY_CHOICES = [
        ("film", "Film"),
        ("serial", "Serial"),
        ("gra", "Gra"),
        ("aktywnosci", "Aktywności"),
    ]
    FILM_SUBCATEGORY_CHOICES = [
        ("fabularny", "Fabularny"),
        ("animacja", "Animacja"),
        ("dokument", "Dokument"),
        ("biograficzny", "Biograficzny"),
        ("anime", "Anime"),
        ("familijny", "Familijny"),
        ("superbohaterski", "Superbohaterski"),
        ("musical", "Musical"),
        ("swiateczny", "Świąteczny"),
        ("krotkometrazowy", "Krótkometrażowy"),
    ]
    SERIAL_SUBCATEGORY_CHOICES = [
        ("miniserial", "Miniserial"),
        ("sitcom", "Sitcom"),
        ("dramatyczny", "Dramatyczny"),
        ("kryminalny", "Kryminalny"),
        ("animowany", "Animowany"),
        ("dokumentalny", "Dokumentalny"),
        ("anime", "Anime"),
        ("antologia", "Antologia"),
        ("procedural", "Procedural"),
        ("young_adult", "Young Adult"),
    ]
    GAME_SUBCATEGORY_CHOICES = [
        ("gra_wideo", "Gra wideo"),
        ("planszowa", "Planszowa"),
        ("karciana", "Karciana"),
        ("imprezowa", "Imprezowa"),
        ("kooperacyjna", "Kooperacyjna"),
        ("rywalizacyjna", "Rywalizacyjna"),
        ("logiczna", "Logiczna"),
        ("mobilna", "Mobilna"),
        ("rpg", "RPG"),
        ("quizowa", "Quizowa"),
    ]
    ACTIVITY_SUBCATEGORY_CHOICES = [
        ("domowa", "Domowa"),
        ("na_miescie", "Na mieście"),
        ("plenerowa", "Plenerowa"),
        ("sportowa", "Sportowa"),
        ("kreatywna", "Kreatywna"),
        ("kulinarna", "Kulinarna"),
        ("relaksacyjna", "Relaksacyjna"),
        ("kulturalna", "Kulturalna"),
        ("towarzyska", "Towarzyska"),
        ("sezonowa", "Sezonowa"),
    ]
    CATEGORY_DETAIL_CONFIG = {
        # Każda kategoria dostaje własny zestaw:
        # label pola, komunikat walidacji, scope tagów i listę podkategorii.
        # Dzięki temu widoki i formularz nie muszą mieć osobnych ifów dla każdej kategorii.
        "film": {
            "subcategory_label": "Podkategoria filmu",
            "subcategory_required_message": "Wybierz podkategorię filmu.",
            "tag_group_label": "Tagi filmowe",
            "tag_scope": "film",
            "choices": FILM_SUBCATEGORY_CHOICES,
            "timing": {
                "label": "Czas trwania (w minutach)",
                "required_message": "Podaj czas trwania filmu.",
                "mode": "minutes",
                "min": "15",
                "step": "15",
                "placeholder": "Np. 90",
            },
        },
        "serial": {
            "subcategory_label": "Podkategoria serialu",
            "subcategory_required_message": "Wybierz podkategorię serialu.",
            "tag_group_label": "Tagi serialowe",
            "tag_scope": "serial",
            "choices": SERIAL_SUBCATEGORY_CHOICES,
            "timing": {
                "label": "Liczba sezonów",
                "required_message": "Podaj liczbę sezonów.",
                "mode": "seasons",
                "min": "1",
                "step": "1",
                "placeholder": "Np. 3",
            },
        },
        "gra": {
            "subcategory_label": "Podkategoria gry",
            "subcategory_required_message": "Wybierz podkategorię gry.",
            "tag_group_label": "Tagi growe",
            "tag_scope": "gra",
            "choices": GAME_SUBCATEGORY_CHOICES,
            "timing": {
                "label": "Czas trwania (w godzinach)",
                "required_message": "Podaj czas trwania gry.",
                "mode": "hours",
                "min": "0.5",
                "step": "0.5",
                "placeholder": "Np. 2",
            },
        },
        "aktywnosci": {
            "subcategory_label": "Podkategoria aktywności",
            "subcategory_required_message": "Wybierz podkategorię aktywności.",
            "tag_group_label": "Tagi aktywności",
            "tag_scope": "aktywnosci",
            "choices": ACTIVITY_SUBCATEGORY_CHOICES,
        },
    }
    VIBE_CHOICES = [
        ("spokojny", "Na spokojny wieczór"),
        ("ekipa", "Z ekipą"),
        ("romantycznie", "Romantycznie"),
        ("budzetowo", "Budżetowo"),
        ("w_domu", "W domu"),
        ("na_miescie", "Na mieście"),
    ]
    COST_CHOICES = [
        ("free", "Za darmo"),
        ("cheap", "Tanie"),
        ("medium", "Średni budżet"),
    ]
    GROUP_SIZE_CHOICES = [
        ("solo", "Solo"),
        ("duo", "2 osoby"),
        ("group", "Grupa"),
    ]
    WEATHER_CHOICES = [
        ("rain", "Na deszcz"),
        ("sun", "Na słoneczny dzień"),
        ("any", "Na każdą pogodę"),
    ]
    SETTING_CHOICES = [
        ("home", "W domu"),
        ("outside", "Na mieście"),
        ("flex", "Dowolnie"),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="film")
    subcategory = models.CharField(max_length=30, blank=True)
    title = models.CharField(max_length=75)
    body = models.TextField(verbose_name="Krótki opis")
    vibe = models.CharField(max_length=20, choices=VIBE_CHOICES, default="spokojny")
    duration_minutes = models.PositiveIntegerField(default=90, verbose_name="Czas trwania (min)")
    season_count = models.PositiveIntegerField(default=1, verbose_name="Liczba sezonów")
    cost_level = models.CharField(max_length=20, choices=COST_CHOICES, default="cheap")
    group_size = models.CharField(max_length=20, choices=GROUP_SIZE_CHOICES, default="group")
    weather_fit = models.CharField(max_length=20, choices=WEATHER_CHOICES, default="any")
    setting = models.CharField(max_length=20, choices=SETTING_CHOICES, default="home")
    pick_reason = models.CharField(
        max_length=140,
        default="Dobry wybór, gdy nie chce wam się długo planować.",
        verbose_name="Powód wyboru",
    )
    tags = models.ManyToManyField(CatalogTag, related_name="posts", blank=True)
    slug = models.SlugField(unique=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    banner = models.ImageField(default="fallback.png", blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.title

    @classmethod
    def category_detail_config(cls, category):
        return cls.CATEGORY_DETAIL_CONFIG.get(category, {})

    @classmethod
    def subcategory_choices(cls, category):
        # Formularz i widoki pytają model o listę opcji,
        # więc cała wiedza o podkategoriach siedzi tutaj, a nie w kilku plikach naraz.
        return cls.category_detail_config(category).get("choices", [])

    @classmethod
    def subcategory_form_label(cls, category):
        return cls.category_detail_config(category).get("subcategory_label", "Podkategoria")

    @classmethod
    def category_tag_group_label(cls, category):
        return cls.category_detail_config(category).get("tag_group_label", "")

    @classmethod
    def category_specific_tag_scope(cls, category):
        return cls.category_detail_config(category).get("tag_scope", "")

    @classmethod
    def category_timing_config(cls, category):
        return cls.category_detail_config(category).get("timing", {})

    @classmethod
    def has_timing_field(cls, category):
        return bool(cls.category_timing_config(category))

    @classmethod
    def timing_form_label(cls, category):
        return cls.category_timing_config(category).get("label", "Czas")

    @classmethod
    def timing_required_message(cls, category):
        return cls.category_timing_config(category).get("required_message", "Podaj czas.")

    @classmethod
    def timing_input_mode(cls, category):
        return cls.category_timing_config(category).get("mode", "")

    @classmethod
    def subcategory_required_message(cls, category):
        return cls.category_detail_config(category).get("subcategory_required_message", "Wybierz podkategorię.")

    @classmethod
    def allowed_tag_scopes(cls, category):
        # Każda kategoria widzi własne tagi i tagi wspólne,
        # żeby formularz był elastyczny, ale nadal miał sensowne granice.
        scopes = {"shared"}
        specific_scope = cls.category_specific_tag_scope(category)
        if specific_scope:
            scopes.add(specific_scope)
        return scopes

    def save(self, *args, **kwargs):
        # Link do wpisu ma brać się z tytułu, ale musi zostać unikalny,
        # nawet jeśli kilka osób doda bardzo podobne propozycje.
        if not self.slug:
            base_slug = slugify(self.title) or "katalog"
            slug = base_slug
            counter = 1
            while Post.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @staticmethod
    def _polish_count_label(count, singular, paucal, plural):
        # Odmianę liczebników ogarniamy w jednym miejscu,
        # bo te etykiety wracają na kartach i w szczególe wpisu.
        if count == 1:
            return f"{count} {singular}"
        if 2 <= count % 10 <= 4 and not 12 <= count % 100 <= 14:
            return f"{count} {paucal}"
        return f"{count} {plural}"

    @property
    def duration_label(self):
        # To jest pomocnicza etykieta do czytelnego pokazywania minut w katalogu.
        # Nawet jeśli część pól nie jest dziś eksponowana, logika formatująca zostaje w modelu.
        minutes = self.duration_minutes or 0
        if minutes < 60:
            return f"{minutes} min"

        hours, remainder = divmod(minutes, 60)
        if remainder == 0:
            return f"{hours} h"
        return f"{hours} h {remainder} min"

    @property
    def season_count_label(self):
        # Osobna etykieta dla seriali pozwala zachować poprawną odmianę sezonów
        # bez przerzucania tej logiki do szablonów.
        count = self.season_count or 0
        if count == 1:
            return "1 sezon"
        if 2 <= count % 10 <= 4 and not 12 <= count % 100 <= 14:
            return f"{count} sezony"
        return f"{count} sezonów"

    @property
    def game_duration_label(self):
        # Gry zapisujemy wewnętrznie w minutach,
        # ale na karcie lepiej brzmią w godzinach, często z jedną cyfrą po przecinku.
        minutes = self.duration_minutes or 0
        if not minutes:
            return ""

        hours = (Decimal(minutes) / Decimal(60)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        if hours == hours.to_integral():
            return f"{int(hours)} h"
        return f"{str(hours).replace('.', ',')} h"

    @property
    def catalog_timing_label(self):
        # To jest wspólny "punkt wejścia" dla widoku:
        # szablon nie musi wiedzieć, czy ma pokazać minuty, sezony czy godziny.
        if self.category == "film":
            return self.duration_label
        if self.category == "serial":
            return self.season_count_label
        if self.category == "gra":
            return self.game_duration_label
        return ""

    @property
    def subcategory_label(self):
        # W bazie trzymamy krótką wartość techniczną,
        # a do UI zawsze chcemy pokazać ładną etykietę dla człowieka.
        return dict(self.subcategory_choices(self.category)).get(self.subcategory, self.subcategory)

    @property
    def display_tags(self):
        # Karta ma pokazywać tylko kilka najmocniejszych sygnałów,
        # bo przy większej liczbie tagów robi się wizualny chaos.
        return list(self.tags.all()[:4])

    @property
    def favorite_total(self):
        # Gdy mamy adnotację z widoku, korzystamy z niej,
        # a w innych miejscach spokojnie spadamy do zwykłego count().
        return getattr(self, "favorite_count", None) if getattr(self, "favorite_count", None) is not None else self.favorited_by.count()

    @property
    def forum_total(self):
        # To samo podejście co przy ulubionych:
        # najpierw bierzemy gotowe zliczenie, a dopiero potem relację z modelu.
        return getattr(self, "forum_count", None) if getattr(self, "forum_count", None) is not None else self.forum_posts.count()

    @property
    def favorite_count_label(self):
        # Gotowa etykieta dla kart i szczegółu wpisu,
        # żeby szablony nie sklejały liczby i tekstu same.
        return self._polish_count_label(self.favorite_total, "osoba zapisała", "osoby zapisały", "osób zapisało")

    @property
    def forum_count_label(self):
        # Analogicznie przygotowujemy etykietę forum,
        # bo ta sama informacja wraca w kilku miejscach interfejsu.
        return self._polish_count_label(self.forum_total, "wątek na forum", "wątki na forum", "wątków na forum")

    @property
    def forum_status_label(self):
        # Zamiast surowego zera dajemy łagodniejszy komunikat,
        # żeby karta brzmiała bardziej naturalnie, gdy nikt jeszcze nie zaczął rozmowy.
        if self.forum_total:
            return self.forum_count_label
        return "Jeszcze cisza na forum"


class FavoritePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_posts")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} -> {self.post.title}"
