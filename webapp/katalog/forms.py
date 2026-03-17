from django import forms 
from . import models 

class CreatePost(forms.ModelForm): 
    class Meta: 
        model = models.Post
        fields = ['category', 'title', 'banner', 'body']
        labels = {
            'category': 'Kategoria',
            'title': 'Tytuł',
            'banner': 'Okładka',
            'body': 'Krótki opis',
        }
        widgets = {
            'category': forms.Select(),
            'title': forms.TextInput(attrs={'placeholder': 'Np. Interstellar'}),
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Dodaj krótki opis pozycji do katalogu'}),
        }
