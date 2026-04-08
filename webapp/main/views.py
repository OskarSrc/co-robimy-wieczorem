# Plik do definiowania widoków, które są renderowane za pomocą szablonizatora Jinja oraz wyświetlane w przeglądarce

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db.models import Count
from django.contrib import messages #to show message back for errors
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from katalog.models import Post
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile
from django.contrib.auth import update_session_auth_hash
from .forms import CustomPasswordChangeForm
import requests
import os
from datetime import date, timedelta


# Create your views here.
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
    return render(request, 'main/clubs.html')

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
    tmdb_key = os.getenv('TMDB_API_KEY')
    rawg_key = os.getenv('RAWG_API_KEY')

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
