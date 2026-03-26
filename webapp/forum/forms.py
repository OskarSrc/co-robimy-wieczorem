from django import forms

from katalog.models import Post

from .models import ForumPost


class CreateForumPost(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ["catalog_post", "subject", "body"]
        labels = {
            "catalog_post": "Pozycja z katalogu",
            "subject": "Temat",
            "body": "Opis",
        }
        widgets = {
            "catalog_post": forms.Select(),
            "subject": forms.TextInput(attrs={"placeholder": "Np. Czy warto obejrzeć w weekend?"}),
            "body": forms.Textarea(attrs={"rows": 6, "placeholder": "Dodaj treść posta i zacznij dyskusję."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["catalog_post"].queryset = Post.objects.order_by("title")
