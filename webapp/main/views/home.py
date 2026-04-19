from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from katalog.models import Post
from main.forms import VotingForm, VotingRoomForm
from main.models import VotingRoom, VotingRoomItem, VotingVote


def get_room_status_text(room, participants_total, votes_total, current_time):
    if participants_total and votes_total >= participants_total:
        return "Wszyscy oddali głosy"
    if current_time >= room.closes_at:
        return "Czas pokoju minął"

    remaining = room.closes_at - current_time
    total_minutes = max(1, int(remaining.total_seconds() // 60))
    hours, minutes = divmod(total_minutes, 60)

    if hours and minutes:
        return f"Jeszcze {hours} godz. {minutes} min"
    if hours:
        return f"Jeszcze {hours} godz."
    return f"Jeszcze {total_minutes} min"


def get_user_rooms(user):
    rooms = list(
        VotingRoom.objects.filter(participants=user)
        .select_related("creator")
        .prefetch_related("participants", "room_items__post", "votes")
        .distinct()
    )

    current_time = timezone.now()

    for room in rooms:
        participants = list(room.participants.all())
        room_items = list(room.room_items.all())
        votes = list(room.votes.all())

        room.participants_total = len(participants)
        room.items_total = len(room_items)
        room.votes_total = len(votes)
        room.is_finished_now = current_time >= room.closes_at or (
            room.participants_total and room.votes_total >= room.participants_total
        )
        room.remaining_votes = max(room.participants_total - room.votes_total, 0)
        room.status_text = get_room_status_text(
            room,
            room.participants_total,
            room.votes_total,
            current_time,
        )

    return rooms


def get_voting_room_or_404(room_id, user):
    return get_object_or_404(
        VotingRoom.objects.select_related("creator").prefetch_related(
            "participants",
            "room_items__post",
            "votes__voter",
            "votes__room_item__post",
        ),
        pk=room_id,
        participants=user,
    )


def build_voting_room_context(room, user, vote_form=None):
    participants = list(room.participants.all().order_by("username"))
    room_items = list(room.room_items.all())
    votes = list(room.votes.all())
    current_time = timezone.now()

    participants_total = len(participants)
    votes_total = len(votes)
    room_finished = current_time >= room.closes_at or (
        participants_total and votes_total >= participants_total
    )

    vote_by_user = {}
    vote_counts = {}

    for vote in votes:
        vote_by_user[vote.voter_id] = vote
        vote_counts[vote.room_item_id] = vote_counts.get(vote.room_item_id, 0) + 1

    for participant in participants:
        participant.current_vote = vote_by_user.get(participant.id)

    highest_score = max(vote_counts.values(), default=0)
    winning_items = []

    for room_item in room_items:
        room_item.votes_total = vote_counts.get(room_item.id, 0)
        room_item.is_winner = room_finished and highest_score > 0 and room_item.votes_total == highest_score
        if room_item.is_winner:
            winning_items.append(room_item)

    current_vote = vote_by_user.get(user.id)
    if vote_form is None:
        initial = {}
        if current_vote and not room_finished:
            initial["room_item"] = current_vote.room_item_id
        vote_form = VotingForm(room, initial=initial or None)

    return {
        "room": room,
        "participants": participants,
        "room_items": room_items,
        "winning_items": winning_items,
        "current_vote": current_vote,
        "vote_form": vote_form,
        "room_finished": room_finished,
        "room_status_text": get_room_status_text(room, participants_total, votes_total, current_time),
        "participants_total": participants_total,
        "votes_total": votes_total,
        "remaining_votes": max(participants_total - votes_total, 0),
    }


def index(request):
    return render(request, "main/index.html")


@login_required
def cars(request):
    values = {
        "cars": [
            {
                "car": "Nissan 350Z",
                "year": 2003,
                "drive_wheel": "rwd",
                "color": "orange",
                "price": "$35,000",
            },
            {
                "car": "Mitsubishi Lancer Evolution VIII",
                "year": 2004,
                "drive_wheel": "4wd",
                "color": "yellow",
                "price": "$36,000",
            },
            {
                "car": "Ford Mustang GT (Gen. 5)",
                "year": 2005,
                "drive_wheel": "rwd",
                "color": "red",
                "price": "$36,000",
            },
            {
                "car": "BMW M3 GTR (E46)",
                "year": 2005,
                "drive_wheel": "rwd",
                "color": "blue and gray",
                "price": "Priceless",
            },
        ]
    }

    return render(request, "main/cars.html", values)


def about(request):
    return render(request, "main/about.html")


def community(request):
    return render(request, "main/community.html")


def voting_rooms(request):
    active_rooms = []
    finished_rooms = []

    if request.user.is_authenticated:
        user_rooms = get_user_rooms(request.user)
        active_rooms = [room for room in user_rooms if not room.is_finished_now]
        finished_rooms = [room for room in user_rooms if room.is_finished_now]

    return render(
        request,
        "main/voting_rooms/index.html",
        {
            "active_rooms": active_rooms,
            "finished_rooms": finished_rooms,
        },
    )


@login_required
def voting_room_new(request):
    if request.method == "POST":
        room_form = VotingRoomForm(request.user, request.POST)
        if room_form.is_valid():
            duration_minutes = room_form.cleaned_data["duration_minutes"]

            with transaction.atomic():
                room = VotingRoom.objects.create(
                    name=room_form.cleaned_data["name"],
                    creator=request.user,
                    closes_at=timezone.now() + timedelta(minutes=duration_minutes),
                )
                room.participants.add(request.user, *list(room_form.cleaned_data["friends"]))
                VotingRoomItem.objects.bulk_create(
                    [
                        VotingRoomItem(room=room, post=post)
                        for post in room_form.cleaned_data["posts"]
                    ]
                )

            return redirect("voting_room_detail", room_id=room.id)
    else:
        room_form = VotingRoomForm(request.user)

    return render(request, "main/voting_rooms/new.html", {"room_form": room_form})


@login_required
def voting_room_detail(request, room_id):
    room = get_voting_room_or_404(room_id, request.user)
    return render(
        request,
        "main/voting_rooms/detail.html",
        build_voting_room_context(room, request.user),
    )


@login_required
def submit_room_vote(request, room_id):
    room = get_voting_room_or_404(room_id, request.user)

    if request.method != "POST":
        return redirect("voting_room_detail", room_id=room.id)

    participants_total = room.participants.count()
    votes_total = room.votes.count()
    room_finished = timezone.now() >= room.closes_at or (
        participants_total and votes_total >= participants_total
    )

    if room_finished:
        return redirect("voting_room_detail", room_id=room.id)

    vote_form = VotingForm(room, request.POST)
    if vote_form.is_valid():
        VotingVote.objects.update_or_create(
            room=room,
            voter=request.user,
            defaults={"room_item": vote_form.cleaned_data["room_item"]},
        )
        return redirect("voting_room_detail", room_id=room.id)

    return render(
        request,
        "main/voting_rooms/detail.html",
        build_voting_room_context(room, request.user, vote_form),
    )


def recommendations(request):
    posts = list(
        Post.objects.annotate(
            favorites_count=Count("favorited_by", distinct=True),
            forum_topics_count=Count("forum_posts", distinct=True),
        )
    )

    for post in posts:
        post.recommendation_score = post.favorites_count + post.forum_topics_count

    recommended_posts = sorted(
        posts,
        key=lambda post: (
            post.recommendation_score,
            post.forum_topics_count,
            post.favorites_count,
            post.date,
        ),
        reverse=True,
    )[:6]

    return render(
        request,
        "main/recommendations.html",
        {"recommended_posts": recommended_posts},
    )