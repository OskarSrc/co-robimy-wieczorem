# Plik do definiowania widoków, które są renderowane za pomocą szablonizatora Jinja oraz wyświetlane w przeglądarce

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import transaction
from django.db.models import Count
from django.contrib import messages #to show message back for errors
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from katalog.models import Post
from .forms import (
    CustomPasswordChangeForm,
    ProfileUpdateForm,
    UserUpdateForm,
    VotingForm,
    VotingRoomForm,
    ClubForm,
)
from .models import Club, FriendRequest, Profile, VotingRoom, VotingRoomItem, VotingVote
from django.contrib.auth import update_session_auth_hash
import requests
import os
from datetime import date, timedelta
# Wczesniej byl w .env ale zapomnialem, że wykładowczyni musi widzieć efekt strony więc jest publiczny teraz.
tmdb_key = os.getenv('TMDB_API_KEY', '66e04b4f6358d30ea3723852498abc1f')
rawg_key = os.getenv('RAWG_API_KEY', 'dd42fbb3cb5a4e179856baa0b34521e1')

# Create your views here.

def get_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def get_room_status_text(room, participants_total, votes_total, current_time):
    if participants_total and votes_total >= participants_total:
        return 'Wszyscy oddali głosy'
    if current_time >= room.closes_at:
        return 'Czas pokoju minął'

    remaining = room.closes_at - current_time
    total_minutes = max(1, int(remaining.total_seconds() // 60))
    hours, minutes = divmod(total_minutes, 60)

    if hours and minutes:
        return f'Jeszcze {hours} godz. {minutes} min'
    if hours:
        return f'Jeszcze {hours} godz.'
    return f'Jeszcze {total_minutes} min'


def get_user_rooms(user):
    rooms = list(
        VotingRoom.objects.filter(participants=user)
        .select_related('creator')
        .prefetch_related('participants', 'room_items__post', 'votes')
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
        VotingRoom.objects.select_related('creator').prefetch_related(
            'participants',
            'room_items__post',
            'votes__voter',
            'votes__room_item__post',
        ),
        pk=room_id,
        participants=user,
    )


def build_voting_room_context(room, user, vote_form=None):
    participants = list(room.participants.all().order_by('username'))
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
            initial['room_item'] = current_vote.room_item_id
        vote_form = VotingForm(room, initial=initial or None)

    return {
        'room': room,
        'participants': participants,
        'room_items': room_items,
        'winning_items': winning_items,
        'current_vote': current_vote,
        'vote_form': vote_form,
        'room_finished': room_finished,
        'room_status_text': get_room_status_text(room, participants_total, votes_total, current_time),
        'participants_total': participants_total,
        'votes_total': votes_total,
        'remaining_votes': max(participants_total - votes_total, 0),
    }

def index(request):
    return render(request, 'main/index.html')

@login_required
def cars(request):
    values = {
        'cars': [
            {
                'car': 'Nissan 350Z',
                'year': 2003,
                'drive_wheel': 'rwd',
                'color': 'orange',
                'price': '$35,000',
            },
            {
                'car': 'Mitsubishi Lancer Evolution VIII',
                'year': 2004,
                'drive_wheel': '4wd',
                'color': 'yellow',
                'price': '$36,000',
            },
            {
                'car': 'Ford Mustang GT (Gen. 5)',
                'year': 2005,
                'drive_wheel': 'rwd',
                'color': 'red',
                'price': '$36,000',
            },
            {
                'car': 'BMW M3 GTR (E46)',
                'year': 2005,
                'drive_wheel': 'rwd',
                'color': 'blue and gray',
                'price': 'Priceless',
            },
        ]
    }

    return render(request, 'main/cars.html', values)

def about(request):
    return render(request, 'main/about.html')

def community(request):
    return render(request, 'main/community.html')

def voting_rooms(request):
    active_rooms = []
    finished_rooms = []

    if request.user.is_authenticated:
        user_rooms = get_user_rooms(request.user)
        active_rooms = [room for room in user_rooms if not room.is_finished_now]
        finished_rooms = [room for room in user_rooms if room.is_finished_now]

    return render(request, 'main/voting_rooms/index.html', {
        'active_rooms': active_rooms,
        'finished_rooms': finished_rooms,
    })


@login_required
def voting_room_new(request):
    if request.method == 'POST':
        room_form = VotingRoomForm(request.user, request.POST)
        if room_form.is_valid():
            duration_minutes = room_form.cleaned_data['duration_minutes']

            with transaction.atomic():
                room = VotingRoom.objects.create(
                    name=room_form.cleaned_data['name'],
                    creator=request.user,
                    closes_at=timezone.now() + timedelta(minutes=duration_minutes),
                )
                room.participants.add(request.user, *list(room_form.cleaned_data['friends']))
                VotingRoomItem.objects.bulk_create([
                    VotingRoomItem(room=room, post=post)
                    for post in room_form.cleaned_data['posts']
                ])

            return redirect('voting_room_detail', room_id=room.id)
    else:
        room_form = VotingRoomForm(request.user)

    return render(request, 'main/voting_rooms/new.html', {'room_form': room_form})


@login_required
def voting_room_detail(request, room_id):
    room = get_voting_room_or_404(room_id, request.user)
    return render(
        request,
        'main/voting_rooms/detail.html',
        build_voting_room_context(room, request.user),
    )


@login_required
def submit_room_vote(request, room_id):
    room = get_voting_room_or_404(room_id, request.user)

    if request.method != 'POST':
        return redirect('voting_room_detail', room_id=room.id)

    participants_total = room.participants.count()
    votes_total = room.votes.count()
    room_finished = timezone.now() >= room.closes_at or (
        participants_total and votes_total >= participants_total
    )

    if room_finished:
        return redirect('voting_room_detail', room_id=room.id)

    vote_form = VotingForm(room, request.POST)
    if vote_form.is_valid():
        VotingVote.objects.update_or_create(
            room=room,
            voter=request.user,
            defaults={'room_item': vote_form.cleaned_data['room_item']},
        )
        return redirect('voting_room_detail', room_id=room.id)

    return render(
        request,
        'main/voting_rooms/detail.html',
        build_voting_room_context(room, request.user, vote_form),
    )

def recommendations(request):
    # Dla każdego wpisu liczymy osobno liczbę ulubionych i liczbę tematów na forum.
    posts = list(
        Post.objects.annotate(
            favorites_count=Count("favorited_by", distinct=True),
            forum_topics_count=Count("forum_posts", distinct=True),
        )
    )

    for post in posts:
        # Prosty wynik polecajki to suma dwóch aktywności społeczności.
        post.recommendation_score = post.favorites_count + post.forum_topics_count

    # Sortujemy od najwyższego wyniku i pokazujemy tylko kilka najmocniejszych propozycji.
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

    # Do szablonu przekazujemy gotową listę wpisów do pokazania.
    return render(
        request,
        'main/recommendations.html',
        {'recommended_posts': recommended_posts},
    )

def clubs(request):
    clubs_list = Club.objects.all()
    club_form = ClubForm() if request.user.is_superuser else None
    return render(request, 'main/clubs/index.html', {
        'clubs': clubs_list,
        'club_form': club_form
    })

@login_required
def club_new(request):
    if not request.user.is_superuser:
        return redirect('clubs')
    
    if request.method == 'POST':
        club_form = ClubForm(request.POST)
        if club_form.is_valid():
            club_form.save()
            return redirect('clubs')
    else:
        club_form = ClubForm()
    
    return render(request, 'main/clubs/new.html', {'club_form': club_form})

def club_detail(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    members = club.members.all()
    posts = club.posts.all()
    return render(request, 'main/clubs/detail.html', {
        'club': club,
        'members': members,
        'posts': posts
    })

@login_required
def join_club(request, club_id):
    """Dołącz do klubu. Jeśli user już ma klub, poproś o potwierdzenie."""
    club = get_object_or_404(Club, id=club_id)
    profile = get_profile(request.user)
    
    # Jeśli user już należy do tego klubu, redirect
    if profile.club_id == club.id:
        return redirect('club_detail', club_id=club.id)
    
    # Jeśli user ma inny klub, poproś o potwierdzenie
    if profile.club_id:
        return redirect('confirm_club_switch', old_club_id=profile.club_id, new_club_id=club.id)
    
    # Dołącz do klubu
    profile.club = club
    profile.save()
    messages.success(request, f'Dołączyłeś do klubu {club.name}!')
    return redirect('club_detail', club_id=club.id)

@login_required
def leave_club(request, club_id):
    """Opuść klub."""
    club = get_object_or_404(Club, id=club_id)
    profile = get_profile(request.user)
    
    if profile.club_id == club.id:
        profile.club = None
        profile.save()
        messages.success(request, f'Opuściłeś klub {club.name}!')
    
    return redirect('club_detail', club_id=club.id)

@login_required
def confirm_club_switch(request, old_club_id, new_club_id):
    """Potwierdź zmianę klubu."""
    old_club = get_object_or_404(Club, id=old_club_id)
    new_club = get_object_or_404(Club, id=new_club_id)
    profile = get_profile(request.user)
    
    # Sprawdź czy user rzeczywiście należy do starego klubu
    if profile.club_id != old_club.id:
        return redirect('club_detail', club_id=new_club.id)
    
    if request.method == 'POST':
        if request.POST.get('confirm') == 'yes':
            # Opuść stary klub i dołącz do nowego
            profile.club = new_club
            profile.save()
            messages.success(request, f'Opuściłeś {old_club.name} i dołączyłeś do {new_club.name}!')
            return redirect('club_detail', club_id=new_club.id)
        else:
            # Anuluj
            return redirect('club_detail', club_id=old_club.id)
    
    return render(request, 'main/clubs/confirm_switch.html', {
        'old_club': old_club,
        'new_club': new_club,
    })

# Using the Django authentication system (Django Documentation)
# https://docs.djangoproject.com/en/5.1/topics/auth/default/
def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
     
    if request.method == 'POST':
         user = authenticate(username=request.POST['username'], password=request.POST['password'])
         if user is not None:
             login(request, user)
             if request.session.get('next'):
                return redirect(request.session.pop('next'))
             
             return redirect('home')
         else:
             messages.error(request, 'Invalid credentials')
             return redirect('login_user')
         
    if request.GET.get('next'):
        request.session['next'] = request.GET['next']

    return render(request, 'main/users/login.html')

def register(request):
    if request.user.is_authenticated:
         return redirect('home')
    
    if request.method == 'POST':
        user = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])
        login(request, user)
        return redirect('home')
    
    return render(request, 'main/users/register.html')

def logout_user(request):
    logout(request)
     
    return redirect('home')

@login_required
def friends_list(request):
    profile = get_profile(request.user)
    friends = profile.friends.all()
    incoming_requests = FriendRequest.objects.filter(to_user=request.user)
    outgoing_requests = FriendRequest.objects.filter(from_user=request.user)
    friend_ids = set(friends.values_list('user_id', flat=True))
    incoming_ids = set(incoming_requests.values_list('from_user_id', flat=True))
    outgoing_ids = set(outgoing_requests.values_list('to_user_id', flat=True))
    suggested_users = User.objects.exclude(pk=request.user.pk).exclude(pk__in=friend_ids).exclude(pk__in=incoming_ids).exclude(pk__in=outgoing_ids).order_by('username')

    query = request.GET.get('q', '').strip()
    if query:
        suggested_users = suggested_users.filter(username__icontains=query)

    return render(request, 'main/users/friends.html', {
        'friends': friends,
        'incoming_requests': incoming_requests,
        'outgoing_requests': outgoing_requests,
        'suggested_users': suggested_users,
        'search_query': query,
    })

@login_required
def send_friend_request(request, user_id):
    if request.method != 'POST':
        return redirect('friends_list')

    target_user = get_object_or_404(User, pk=user_id)
    if target_user == request.user:
        return redirect('friends_list')

    sender_profile = get_profile(request.user)
    receiver_profile = get_profile(target_user)

    if receiver_profile in sender_profile.friends.all():
        return redirect('friends_list')

    existing_request = FriendRequest.objects.filter(from_user=target_user, to_user=request.user).first()
    if existing_request:
        existing_request.accept()
        return redirect('friends_list')

    FriendRequest.objects.get_or_create(from_user=request.user, to_user=target_user)
    return redirect('friends_list')

@login_required
def cancel_friend_request(request, user_id):
    if request.method != 'POST':
        return redirect('friends_list')

    target_user = get_object_or_404(User, pk=user_id)
    FriendRequest.objects.filter(from_user=request.user, to_user=target_user).delete()
    return redirect('friends_list')

@login_required
def accept_friend_request(request, request_id):
    if request.method != 'POST':
        return redirect('friends_list')

    friend_request = get_object_or_404(FriendRequest, pk=request_id, to_user=request.user)
    friend_request.accept()
    return redirect('friends_list')

@login_required
def decline_friend_request(request, request_id):
    if request.method != 'POST':
        return redirect('friends_list')

    friend_request = get_object_or_404(FriendRequest, pk=request_id, to_user=request.user)
    friend_request.delete()
    return redirect('friends_list')

@login_required
def remove_friend(request, user_id):
    if request.method != 'POST':
        return redirect('friends_list')

    target_user = get_object_or_404(User, pk=user_id)
    profile = get_profile(request.user)
    target_profile = get_profile(target_user)
    profile.friends.remove(target_profile)
    return redirect('friends_list')

@login_required
def profile_user(request):
    Profile.objects.get_or_create(user=request.user)

    u_form = UserUpdateForm(instance=request.user)
    p_form = ProfileUpdateForm(instance=request.user.profile)
    pass_form = CustomPasswordChangeForm(user=request.user)

    if 'update_profile' in request.POST:
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                return redirect('profile_user')

    elif 'change_password' in request.POST:
            pass_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
            if pass_form.is_valid():
                user = pass_form.save()
                update_session_auth_hash(request, user)
                return redirect('profile_user')

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'pass_form': pass_form
    }
    return render(request, 'main/users/profile.html', context)

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)
        return redirect('home')
    
    return redirect('profile_user')

def widok_eventow(request):

    dzisiaj = date.today()
    za_pol_roku = dzisiaj + timedelta(180)

    filmy = []
    try:
        url_filmy = f"https://api.themoviedb.org/3/movie/upcoming?api_key={tmdb_key}&language=pl-PL&page=1"
        #wysyła zapytanie i zapisuje odpowiedź w tej zmiennej
        odp = requests.get(url_filmy, timeout=5)

        #jeśli res ma odp status 200 to sukces
        if odp.status_code == 200:
            dane = odp.json()
            #jeśli coś się zepsuje wysyła bezpieczną pustą liste po stronie strony
            surowa_lista_filmy = dane.get('results', [])[:15]
            # filtrowanie, str zmienia w stringa po prostu
            surowa_lista_filmy = [m for m in surowa_lista_filmy
                                  if m.get('release_date') and m.get('release_date') >= str(dzisiaj)]
            # sortowanie i ucinanie
            filmy = sorted(surowa_lista_filmy, key=lambda film: film.get('release_date', ''))[:20]
        else:
            print("Nie wykryto klucza API.")

    except Exception as error:       
        print(f"Błąd pobierania: {error}")

    gry = []
    if rawg_key:
        try:
            url_gry = f"https://api.rawg.io/api/games?key={rawg_key}&dates={dzisiaj},{za_pol_roku}&ordering=released"
            odp_gry = requests.get(url_gry, timeout=5)
            if odp_gry.status_code == 200:
                dane_gry = odp_gry.json()
                gry = dane_gry.get('results', [])[:15]

        except Exception as error:
            print(f"Błąd pobierania gier: {error}")

    else:
        print("Nie wykryto klucza API.")

    anime = []
    try:
        url_anime = "https://api.jikan.moe/v4/seasons/upcoming"
        odp_anime = requests.get(url_anime, timeout=5)
        
        if odp_anime.status_code == 200:
            dane_anime = odp_anime.json()
            surowa_lista_anime = dane_anime.get('data', [])[:15]

            surowa_lista_anime = [
                a for a in surowa_lista_anime 
                if a.get('aired') and a['aired'].get('from') and a['aired']['from'] >= str(dzisiaj)
            ]
            anime = sorted(surowa_lista_anime, key=lambda a: a['aired']['from'])[:20]
        else:
            print("Nie wykryto klucza API.")

    except Exception as e:
        print(f"Błąd Anime: {e}")        

    return render(request, 'main/events.html', {
        'movies': filmy,
        'games': gry,
        'anime': anime
    })
