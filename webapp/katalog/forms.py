from django import forms

from . import models


class CreatePost(forms.ModelForm):
    # Ten formularz pilnuje, zeby dodatkowy tag anime mial sens tylko przy Anime.
    def clean(self):
        cleaned_data = super().clean()
        tagi = cleaned_data.get("tagi")
        podtag_anime = cleaned_data.get("podtag_anime")

        if tagi != "anime" and podtag_anime:
            cleaned_data["podtag_anime"] = ""

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.tagi != "anime":
            instance.podtag_anime = ""

        if commit:
            instance.save()

        return instance

    class Meta:
        model = models.Post
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
        help_texts = {
            "tagi": "Wybierz jeden prosty tag tematyczny.",
            "podtag_anime": "To pole pojawia sie przy tagu Anime.",
            "cena": "To pole najbardziej przydaje sie przy aktywnosciach.",
        }
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
