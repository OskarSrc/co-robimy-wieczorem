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
