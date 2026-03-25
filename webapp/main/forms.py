from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import PasswordChangeForm

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'style': 'color: white !important;',
                'class': 'form-control text-white bg-transparent'
                }),
            'email': forms.EmailInput(attrs={
                'style': 'color: white !important;',
                'class': 'form-control text-white bg-transparent'
                                             }),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(attrs={
                'style': 'color: white !important;',
                'class': 'form-control text-white bg-transparent border-secondary', 
                'rows': 3, 
                'placeholder': 'Napisz coś o sobie...'
            }),
        }

class CustomPasswordChangeForm (PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control text-white bg-transparent border-secondary',
                'style': 'color: white !important;'
            })