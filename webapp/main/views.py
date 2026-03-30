# Plik do definiowania widoków, które są renderowane za pomocą szablonizatora Jinja oraz wyświetlane w przeglądarce

from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages #to show message back for errors
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
from django.utils import timezone

from forum.models import ForumPost
from katalog.models import CatalogTag, Post

from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile
from django.contrib.auth import update_session_auth_hash
from .forms import CustomPasswordChangeForm

# Create your views here.
def index(request):
    return render(request, 'main/index.html')


def community(request):
    # To jest na razie hub społeczności: spina forum z lżejszymi wejściami,
    # zanim powstaną osobne moduły typu kluby czy szukanie ekipy.
    # Każda karta opisuje jedno "wejście" na stronę i może prowadzić
    # albo do gotowej funkcji, albo do sekcji, która pokazuje kierunek rozwoju.
    community_cards = [
        {
            'title': 'Forum',
            'description': 'Dłuższe rozmowy, pytania i tematy od społeczności.',
            'icon': 'fa-comments',
            'href': reverse('forum:index'),
            'cta': 'Przejdź do forum',
        },
        {
            'title': 'Znajdź ekipę',
            'description': 'Szukasz ludzi na film, planszówki, wyjście albo spontaniczny wieczór?',
            'icon': 'fa-user-group',
            'href': '#community-cta',
            'cta': 'Zobacz kierunek',
        },
        {
            'title': 'Polecajki społeczności',
            'description': 'Szybkie rekomendacje od ludzi: co obejrzeć, w co zagrać, gdzie wyjść.',
            'icon': 'fa-heart',
            'href': '#community-top',
            'cta': 'Sprawdź top tygodnia',
        },
        {
            'title': 'Kluby zainteresowań',
            'description': 'Mniejsze miejsca dla osób o podobnym klimacie i zainteresowaniach.',
            'icon': 'fa-mug-hot',
            'href': '#community-climates',
            'cta': 'Wybierz klimat',
        },
    ]

    # Klimaty prowadzą do tego, co już istnieje w katalogu, żeby nie budować
    # pustych podstron tylko po to, żeby zapełnić sekcję.
    # Dzięki temu społeczność od razu łączy się z katalogiem,
    # a nie działa jako zupełnie osobny byt.
    climate_cards = [
        {
            'title': 'Filmowe wieczory',
            'description': 'Kiedy macie ochotę po prostu usiąść i wejść w dobry seans.',
            'href': f"{reverse('posts:list')}?category=film",
        },
        {
            'title': 'Seriale na raz',
            'description': 'Dla tych, którzy lubią mówić „jeszcze tylko jeden odcinek”.',
            'href': f"{reverse('posts:list')}?category=serial",
        },
        {
            'title': 'Granie razem',
            'description': 'Wspólne granie, trochę rywalizacji i trochę śmiechu.',
            'href': f"{reverse('posts:list')}?category=gra",
        },
        {
            'title': 'Spokojne wyjścia',
            'description': 'Pomysły na lżejsze wyjście bez wielkiego planowania.',
            'href': f"{reverse('posts:list')}?category=aktywnosci",
        },
        {
            'title': 'Cozy wieczory',
            'description': 'Ciepły klimat, trochę bliskości i mniej pośpiechu.',
            'href': reverse('posts:theme', args=['top-na-randke']),
        },
        {
            'title': 'Na spontanie',
            'description': 'Szybki skrót do pomysłów, kiedy decyzję trzeba podjąć teraz.',
            'href': reverse('posts:theme', args=['na-dzis']),
        },
    ]

    # Pytanie zmienia się wraz z datą, dzięki czemu strona nie wygląda codziennie tak samo.
    question_options = [
        'Idealny film na deszczowy wieczór?',
        'Domówka czy wyjście?',
        'Co ostatnio was wciągnęło?',
    ]
    question_of_day = question_options[timezone.localdate().toordinal() % len(question_options)]

    # Tu celowo pokazujemy prawdziwe dane z katalogu i forum,
    # żeby społeczność od startu wyglądała jak żywe miejsce.
    top_recommended = (
        Post.objects.select_related('author')
        .prefetch_related('tags')
        .annotate(
            favorite_count=Count('favorited_by', distinct=True),
            forum_count=Count('forum_posts', distinct=True),
        )
        .order_by('-favorite_count', '-forum_count', '-date')[:3]
    )
    # Forum nie ma jeszcze komentarzy pod tematami,
    # więc jako oznakę ruchu pokazujemy po prostu najświeższe wątki.
    top_topics = ForumPost.objects.select_related('catalog_post', 'author').order_by('-created_at')[:3]
    # Tu zbieramy najpopularniejsze tagi wspólne, bo one najlepiej oddają klimat społeczności,
    # a nie tylko jedną kategorię typu film albo gra.
    top_climates = (
        CatalogTag.objects.filter(scope='shared')
        .annotate(posts_count=Count('posts', distinct=True))
        .filter(posts_count__gt=0)
        .order_by('-posts_count', 'sort_order', 'name')[:3]
    )

    # Liczniki w hero mają dawać szybki sygnał, że podstrona jest spięta z resztą projektu,
    # a nie wisi jako osobna, pusta makieta.
    # Wszystko składamy w jeden context, bo szablon ma być już prosty:
    # ma tylko ułożyć sekcje, a nie podejmować decyzje biznesowe.
    context = {
        'community_cards': community_cards,
        'climate_cards': climate_cards,
        'question_of_day': question_of_day,
        'top_recommended': top_recommended,
        'top_topics': top_topics,
        'top_climates': top_climates,
        'forum_posts_count': ForumPost.objects.count(),
        'catalog_posts_count': Post.objects.count(),
        'users_count': User.objects.count(),
    }
    return render(request, 'main/community.html', context)

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
