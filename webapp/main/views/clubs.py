from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import ClubForm
from main.models import Club

from .auth import get_profile


def clubs(request):
    clubs_list = Club.objects.all()
    club_form = ClubForm() if request.user.is_superuser else None
    return render(
        request,
        "main/clubs/index.html",
        {
            "clubs": clubs_list,
            "club_form": club_form,
        },
    )


@login_required
def club_new(request):
    if not request.user.is_superuser:
        return redirect("clubs")

    if request.method == "POST":
        club_form = ClubForm(request.POST)
        if club_form.is_valid():
            club_form.save()
            return redirect("clubs")
    else:
        club_form = ClubForm()

    return render(request, "main/clubs/new.html", {"club_form": club_form})


def club_detail(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    members = club.members.all()
    posts = club.posts.all()
    return render(
        request,
        "main/clubs/detail.html",
        {
            "club": club,
            "members": members,
            "posts": posts,
        },
    )


@login_required
def join_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    profile = get_profile(request.user)

    if profile.club_id == club.id:
        return redirect("club_detail", club_id=club.id)

    if profile.club_id:
        return redirect("confirm_club_switch", old_club_id=profile.club_id, new_club_id=club.id)

    profile.club = club
    profile.save()
    messages.success(request, f"Dołączyłeś do klubu {club.name}!")
    return redirect("club_detail", club_id=club.id)


@login_required
def leave_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    profile = get_profile(request.user)

    if profile.club_id == club.id:
        profile.club = None
        profile.save()
        messages.success(request, f"Opuściłeś klub {club.name}!")

    return redirect("club_detail", club_id=club.id)


@login_required
def confirm_club_switch(request, old_club_id, new_club_id):
    old_club = get_object_or_404(Club, id=old_club_id)
    new_club = get_object_or_404(Club, id=new_club_id)
    profile = get_profile(request.user)

    if profile.club_id != old_club.id:
        return redirect("club_detail", club_id=new_club.id)

    if request.method == "POST":
        if request.POST.get("confirm") == "yes":
            profile.club = new_club
            profile.save()
            messages.success(request, f"Opuściłeś {old_club.name} i dołączyłeś do {new_club.name}!")
            return redirect("club_detail", club_id=new_club.id)

        return redirect("club_detail", club_id=old_club.id)

    return render(
        request,
        "main/clubs/confirm_switch.html",
        {
            "old_club": old_club,
            "new_club": new_club,
        },
    )