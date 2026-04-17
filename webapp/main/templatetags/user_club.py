from django import template
from main.models import Profile

# Ten filtr dorzuca przy nicku kolor i emoji klubu,
# żeby na listach i w komentarzach było od razu widać przynależność użytkownika.
register = template.Library()

@register.filter
def user_with_club(user):
    """Wyświetl nicka usera z kolorem i emotką klubu jeśli użytkownik do niego należy."""
    try:
        profile = Profile.objects.select_related('club').get(user=user)
        if profile.club:
            return f'<span style="color: {profile.club.color};">{user.username} {profile.club.icon}</span>'
        return user.username
    except Profile.DoesNotExist:
        return user.username
