from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

from main.models import Club, Profile


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "style": "color: white !important;",
                    "class": "form-control text-white bg-transparent",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "style": "color: white !important;",
                    "class": "form-control text-white bg-transparent",
                }
            ),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio"]
        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "style": "color: white !important;",
                    "class": "form-control text-white bg-transparent border-secondary",
                    "rows": 3,
                    "placeholder": "Napisz coś o sobie...",
                }
            ),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update(
                {
                    "class": "form-control text-white bg-transparent border-secondary",
                    "style": "color: white !important;",
                }
            )


class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ["name", "description", "color", "icon", "posts"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control bg-transparent text-white border-secondary",
                    "placeholder": "Np. Klub horrorów",
                    "style": "--placeholder-color: rgba(255, 255, 255, 0.9);",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control bg-transparent text-white border-secondary",
                    "rows": 3,
                    "placeholder": "Opisz klimat klubu...",
                    "style": "--placeholder-color: rgba(255, 255, 255, 0.9);",
                }
            ),
            "color": forms.TextInput(
                attrs={
                    "type": "color",
                    "class": "form-control bg-transparent text-white border-secondary",
                }
            ),
            "icon": forms.TextInput(
                attrs={
                    "class": "form-control bg-transparent text-white border-secondary",
                    "placeholder": "Wklej emoji tutaj",
                    "maxlength": "2",
                }
            ),
            "posts": forms.CheckboxSelectMultiple(),
        }