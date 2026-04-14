from django import forms

from katalog.models import Post

from .models import ForumPost, ForumReply


# Formularz modelowy tworzy nowe tematy forum na podstawie modelu `ForumPost`.
class CreateForumPost(forms.ModelForm):
    class Meta:
        # Formularz zapisuje dane bezpośrednio do modelu `ForumPost`.
        model = ForumPost
        # Użytkownik wybiera pozycję z katalogu, wpisuje temat i treść.
        fields = ["catalog_post", "subject", "body"]
        # Etykiety są po polsku, więc formularz jest bardziej zrozumiały.
        labels = {
            "catalog_post": "Pozycja z katalogu",
            "subject": "Temat",
            "body": "Opis",
        }
        # Widgety sterują tym, jak pola są renderowane w HTML.
        widgets = {
            "catalog_post": forms.Select(),
            "subject": forms.TextInput(attrs={"placeholder": "Np. Czy warto obejrzeć w weekend?"}),
            "body": forms.Textarea(attrs={"rows": 6, "placeholder": "Dodaj treść posta i zacznij dyskusję."}),
        }

    def __init__(self, *args, **kwargs):
        # Najpierw budujemy standardowy formularz z klasy bazowej.
        super().__init__(*args, **kwargs)
        # Pozycje z katalogu są sortowane alfabetycznie po tytule.
        self.fields["catalog_post"].queryset = Post.objects.order_by("title")


class EditForumPost(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ["subject", "body"]
        labels = {
            "subject": "Temat",
            "body": "Opis",
        }
        widgets = {
            "subject": forms.TextInput(attrs={"placeholder": "Np. Czy warto obejrzeć w weekend?"}),
            "body": forms.Textarea(attrs={"rows": 6, "placeholder": "Edytuj treść posta."}),
        }


class CreateForumReply(forms.ModelForm):
    class Meta:
        model = ForumReply
        fields = ["body"]
        labels = {
            "body": "Odpowiedź",
        }
        widgets = {
            "body": forms.Textarea(attrs={"rows": 4, "placeholder": "Dodaj swoją odpowiedź..."}),
        }


class EditForumReply(forms.ModelForm):
    class Meta:
        model = ForumReply
        fields = ["body"]
        labels = {
            "body": "Odpowiedź",
        }
        widgets = {
            "body": forms.Textarea(attrs={"rows": 4, "placeholder": "Edytuj odpowiedź..."}),
        }
