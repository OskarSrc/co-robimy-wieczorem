from django import forms

from . import models


class CreatePost(forms.ModelForm):
    # Ten formularz obsługuje zarówno dodawanie, jak i edycję wpisu.
    # Najważniejsza rzecz: część pól zależy od wybranej kategorii,
    # więc nie możemy zostawić go jako "surowego" ModelForm bez własnej logiki.
    subcategory = forms.ChoiceField(
        choices=(),
        required=False,
        label="Podkategoria",
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=models.CatalogTag.objects.none(),
        required=False,
        label="Tagi",
        help_text="Możesz zaznaczyć kilka tagów.",
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = models.Post
        fields = [
            "category",
            "subcategory",
            "title",
            "banner",
            "body",
            "tags",
            "pick_reason",
        ]
        labels = {
            "category": "Kategoria",
            "title": "Tytuł",
            "banner": "Okładka",
            "body": "Krótki opis",
            "pick_reason": "Dlaczego warto",
        }
        widgets = {
            "category": forms.Select(),
            "title": forms.TextInput(attrs={"placeholder": "Np. Interstellar"}),
            "banner": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "body": forms.Textarea(attrs={"rows": 4, "placeholder": "Dodaj krótki opis pozycji do katalogu"}),
            "pick_reason": forms.TextInput(
                attrs={"placeholder": "Np. Dobre, gdy nie chce wam się długo planować."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Wszystkie tagi są ładowane od razu, bo szablon sam rozdziela je
        # na grupę wspólną i grupy kategorii. Dzięki temu formularz nie musi
        # budować osobnych pól dla filmu, serialu, gry i aktywności.
        self.fields["tags"].queryset = models.CatalogTag.objects.order_by("scope", "sort_order", "name")

        # Kategoria może pochodzić z trzech miejsc:
        # 1. z danych POST, gdy użytkownik właśnie wysyła formularz,
        # 2. z initial/instance, gdy edytujemy istniejący wpis,
        # 3. z domyślnej kategorii modelu, gdy dodajemy nowy wpis od zera.
        selected_category = (
            self.data.get("category")
            or self.initial.get("category")
            or getattr(self.instance, "category", "")
            or models.Post._meta.get_field("category").default
        )

        # To jest klucz do "dynamicznego" formularza:
        # lista podkategorii i sama etykieta pola zmieniają się w zależności od kategorii.
        self.fields["subcategory"].choices = models.Post.subcategory_choices(selected_category)
        self.fields["subcategory"].label = models.Post.subcategory_form_label(selected_category)

        # Przy edycji chcemy zobaczyć już zapisaną podkategorię,
        # inaczej select wróciłby do pustej opcji.
        if self.instance and self.instance.pk and self.instance.subcategory:
            self.fields["subcategory"].initial = self.instance.subcategory

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        subcategory = cleaned_data.get("subcategory") or ""
        tags = cleaned_data.get("tags") or []

        # Dla kategorii, które mają własne podkategorie, nie pozwalamy
        # zostawić pustego wyboru, bo wtedy wpis byłby zbyt ogólny.
        if models.Post.subcategory_choices(category) and not subcategory:
            self.add_error("subcategory", models.Post.subcategory_required_message(category))

        # Tagi mają własne "scope", więc tutaj pilnujemy,
        # żeby np. film nie dostał tagu growego.
        allowed_scopes = models.Post.allowed_tag_scopes(category)
        invalid_tags = [tag.name for tag in tags if tag.scope not in allowed_scopes]
        if invalid_tags:
            self.add_error("tags", "Wybrane tagi nie pasują do tej kategorii.")

        # Jeśli kiedyś pojawi się kategoria bez podkategorii,
        # to czyścimy to pole, żeby nie został w nim stary wybór z formularza.
        if not models.Post.subcategory_choices(category):
            cleaned_data["subcategory"] = ""

        return cleaned_data
