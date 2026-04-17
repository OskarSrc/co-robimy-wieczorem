from .models import FriendRequest


# Ten context processor dorzuca do każdego szablonu liczbę oczekujących zaproszeń.
# Dzięki temu pasek nawigacji może pokazać kropkę przy sekcji znajomych.
def pending_friend_requests(request):
    if request.user.is_authenticated:
        # Liczymy tylko zaproszenia przychodzące do zalogowanej osoby.
        pending_count = FriendRequest.objects.filter(to_user=request.user).count()
    else:
        # Dla gościa nie pokazujemy żadnych oczekujących zaproszeń.
        pending_count = 0

    return {
        'pending_friend_requests_count': pending_count,
    }
