from django import forms

from . import models


# Formularz modelowy służy do dodawania i edycji wpisów w katalogu.
class CreatePost(forms.ModelForm):
    # Ta walidacja pilnuje, żeby dodatkowy tag anime miał sens tylko przy tagu Anime.
    def clean(self):
        # `cleaned_data` zawiera dane już wstępnie przetworzone przez Django.
        cleaned_data = super().clean()
        tagi = cleaned_data.get("tagi")
        podtag_anime = cleaned_data.get("podtag_anime")

        # Jeśli wybrano inny tag niż anime, czyścimy dodatkowy podtag.
        if tagi != "anime" and podtag_anime:
            cleaned_data["podtag_anime"] = ""

        return cleaned_data

    def save(self, commit=True):
        # `commit=False` pozwala poprawić dane przed finalnym zapisem do bazy.
        instance = super().save(commit=False)

        # Dla bezpieczeństwa czyścimy podtag także przy samym zapisie formularza.
        if instance.tagi != "anime":
            instance.podtag_anime = ""

        if commit:
            # Zapis wykonuje się tylko wtedy, gdy wywołujący tego oczekuje.
            instance.save()

        return instance

    class Meta:
        # Formularz pracuje bezpośrednio na modelu `Post`.
        model = models.Post
        # Te pola budują pełny formularz dodawania wpisu do katalogu.
        fields = [
            "category",
            "title",
            "tagi",
            "podtag_anime",
            "okazja",
            "liczba_osob",
            "cena",
            "banner",
            "body",
        ]
        # Polskie etykiety sprawiają, że formularz jest czytelniejszy dla użytkownika.
        labels = {
            "category": "Kategoria",
            "title": "Tytu\u0142",
            "tagi": "Tagi",
            "podtag_anime": "Dodatkowy tag anime",
            "okazja": "Okazja",
            "liczba_osob": "Liczba os\u00f3b",
            "cena": "Cena",
            "banner": "Ok\u0142adka",
            "body": "Kr\u00f3tki opis",
        }
        # Krótkie podpowiedzi pomagają zrozumieć mniej oczywiste pola.
        help_texts = {
            "tagi": "Wybierz jeden prosty tag tematyczny.",
        }
        # Widgety kontrolują sposób renderowania pól w HTML.
        widgets = {
            "category": forms.Select(),
            "tagi": forms.Select(),
            "podtag_anime": forms.Select(),
            "okazja": forms.Select(),
            "liczba_osob": forms.Select(),
            "cena": forms.Select(),
            "title": forms.TextInput(attrs={"placeholder": "Np. Interstellar"}),
            "body": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Dodaj krotki opis pozycji do katalogu"}
            ),
        }
