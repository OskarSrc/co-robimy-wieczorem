from django import forms
from django.contrib.auth.models import User

from katalog.models import Post
from main.models import Profile, VotingRoomItem


class FriendChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.username


class CatalogPostChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.title} ({obj.get_category_display()})"


class VotingRoomItemChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.post.title} ({obj.post.get_category_display()})"


class VotingRoomForm(forms.Form):
    DURATION_CHOICES = [
        (15, "15 minut"),
        (30, "30 minut"),
        (60, "1 godzina"),
        (120, "2 godziny"),
    ]

    name = forms.CharField(
        max_length=80,
        label="Nazwa pokoju",
        widget=forms.TextInput(
            attrs={
                "class": "form-control bg-transparent text-white border-secondary",
                "placeholder": "Np. Piątkowy film ze znajomymi",
            }
        ),
    )
    duration_minutes = forms.TypedChoiceField(
        label="Czas trwania",
        choices=DURATION_CHOICES,
        coerce=int,
        initial=60,
        widget=forms.Select(
            attrs={
                "class": "form-select bg-transparent text-white border-secondary",
            }
        ),
    )
    friends = FriendChoiceField(
        queryset=User.objects.none(),
        label="Znajomi",
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )
    posts = CatalogPostChoiceField(
        queryset=Post.objects.none(),
        label="Pozycje z katalogu",
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile, _ = Profile.objects.get_or_create(user=user)
        friend_ids = profile.friends.values_list("user_id", flat=True)
        self.fields["friends"].queryset = User.objects.filter(pk__in=friend_ids).order_by("username")
        self.fields["posts"].queryset = Post.objects.order_by("-date")

    def clean_friends(self):
        friends = self.cleaned_data["friends"]
        if friends.count() < 1:
            raise forms.ValidationError("Wybierz przynajmniej jednego znajomego do pokoju.")
        return friends

    def clean_posts(self):
        posts = self.cleaned_data["posts"]
        if posts.count() < 2:
            raise forms.ValidationError("Wybierz przynajmniej dwie pozycje z katalogu.")
        return posts


class VotingForm(forms.Form):
    room_item = VotingRoomItemChoiceField(
        queryset=VotingRoomItem.objects.none(),
        label="Oddaj głos",
        empty_label=None,
        widget=forms.RadioSelect,
    )

    def __init__(self, room, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["room_item"].queryset = room.room_items.select_related("post")