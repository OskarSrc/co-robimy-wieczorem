from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import CustomPasswordChangeForm, ProfileUpdateForm, UserUpdateForm
from main.models import FriendRequest, Profile


def get_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def login_user(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        user = authenticate(username=request.POST["username"], password=request.POST["password"])
        if user is not None:
            login(request, user)
            if request.session.get("next"):
                return redirect(request.session.pop("next"))

            return redirect("home")

        messages.error(request, "Invalid credentials")
        return redirect("login_user")

    if request.GET.get("next"):
        request.session["next"] = request.GET["next"]

    return render(request, "main/users/login.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, f'Nazwa "{username}" jest już zajęta. Wybierz inną!')
            return render(request, "main/users/register.html")

        try:
            user = User.objects.create_user(username, email, password)
            login(request, user)
            messages.success(request, f"Witaj {username}! Twoje konto zostało utworzone.")
            return redirect("home")
        except Exception:
            messages.error(request, "Wystąpił nieoczekiwany błąd przy tworzeniu konta.")
            return render(request, "main/users/register.html")

    return render(request, "main/users/register.html")


def logout_user(request):
    logout(request)
    return redirect("home")


@login_required
def friends_list(request):
    profile = get_profile(request.user)
    friends = profile.friends.all()
    incoming_requests = FriendRequest.objects.filter(to_user=request.user)
    outgoing_requests = FriendRequest.objects.filter(from_user=request.user)
    friend_ids = set(friends.values_list("user_id", flat=True))
    incoming_ids = set(incoming_requests.values_list("from_user_id", flat=True))
    outgoing_ids = set(outgoing_requests.values_list("to_user_id", flat=True))
    suggested_users = (
        User.objects.exclude(pk=request.user.pk)
        .exclude(pk__in=friend_ids)
        .exclude(pk__in=incoming_ids)
        .exclude(pk__in=outgoing_ids)
        .order_by("username")
    )

    query = request.GET.get("q", "").strip()
    if query:
        suggested_users = suggested_users.filter(username__icontains=query)

    return render(
        request,
        "main/users/friends.html",
        {
            "friends": friends,
            "incoming_requests": incoming_requests,
            "outgoing_requests": outgoing_requests,
            "suggested_users": suggested_users,
            "search_query": query,
        },
    )


@login_required
def send_friend_request(request, user_id):
    if request.method != "POST":
        return redirect("friends_list")

    target_user = get_object_or_404(User, pk=user_id)
    if target_user == request.user:
        return redirect("friends_list")

    sender_profile = get_profile(request.user)
    receiver_profile = get_profile(target_user)

    if receiver_profile in sender_profile.friends.all():
        return redirect("friends_list")

    existing_request = FriendRequest.objects.filter(from_user=target_user, to_user=request.user).first()
    if existing_request:
        existing_request.accept()
        return redirect("friends_list")

    FriendRequest.objects.get_or_create(from_user=request.user, to_user=target_user)
    return redirect("friends_list")


@login_required
def cancel_friend_request(request, user_id):
    if request.method != "POST":
        return redirect("friends_list")

    target_user = get_object_or_404(User, pk=user_id)
    FriendRequest.objects.filter(from_user=request.user, to_user=target_user).delete()
    return redirect("friends_list")


@login_required
def accept_friend_request(request, request_id):
    if request.method != "POST":
        return redirect("friends_list")

    friend_request = get_object_or_404(FriendRequest, pk=request_id, to_user=request.user)
    friend_request.accept()
    return redirect("friends_list")


@login_required
def decline_friend_request(request, request_id):
    if request.method != "POST":
        return redirect("friends_list")

    friend_request = get_object_or_404(FriendRequest, pk=request_id, to_user=request.user)
    friend_request.delete()
    return redirect("friends_list")


@login_required
def remove_friend(request, user_id):
    if request.method != "POST":
        return redirect("friends_list")

    target_user = get_object_or_404(User, pk=user_id)
    profile = get_profile(request.user)
    target_profile = get_profile(target_user)
    profile.friends.remove(target_profile)
    return redirect("friends_list")


@login_required
def profile_user(request):
    Profile.objects.get_or_create(user=request.user)

    u_form = UserUpdateForm(instance=request.user)
    p_form = ProfileUpdateForm(instance=request.user.profile)
    pass_form = CustomPasswordChangeForm(user=request.user)

    if "update_profile" in request.POST:
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect("profile_user")

    elif "change_password" in request.POST:
        pass_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if pass_form.is_valid():
            user = pass_form.save()
            update_session_auth_hash(request, user)
            return redirect("profile_user")

    context = {
        "u_form": u_form,
        "p_form": p_form,
        "pass_form": pass_form,
    }
    return render(request, "main/users/profile.html", context)


@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        logout(request)
        return redirect("home")

    return redirect("profile_user")