from .models import FriendRequest


def pending_friend_requests(request):
    if request.user.is_authenticated:
        pending_count = FriendRequest.objects.filter(to_user=request.user).count()
    else:
        pending_count = 0

    return {
        'pending_friend_requests_count': pending_count,
    }
