from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef, Q
from django.shortcuts import get_object_or_404, redirect, render

from . import forms
from .models import FavoritePost, Post

# Ta funkcja pomocnicza zapisuje wpis zarówno przy dodawaniu, jak i przy edycji.


def _save_post_from_form(form, author):
    # `commit=False` daje chwilę na dopisanie autora przed zapisem do bazy.
    newpost = form.save(commit=False)
    newpost.author = author
    # Po uzupełnieniu autora zapisujemy gotowy obiekt.
    newpost.save()
    return newpost

# Widok listy pokazuje wszystkie wpisy albo tylko wpisy z wybranej kategorii.
def posts_list(request):
    category = request.GET.get('category')
    query = request.GET.get('q', '').strip()
    # Na start pobieramy pełną listę wpisów.
    posts = Post.objects.all()
    if category:
        # Jeśli użytkownik wybrał kategorię, zawężamy wyniki.
        posts = posts.filter(category=category)

    if query:
        posts = posts.filter(
            Q(title__icontains=query)
            | Q(body__icontains=query)
            | Q(tagi__icontains=query)
            | Q(podtag_anime__icontains=query)
        )

    # Losowanie działa na aktualnie widocznym zestawie wpisów, więc szanuje filtry i wyszukiwarkę.
    random_post = posts.order_by('?').first()

    if request.user.is_authenticated:
        # To podzapytanie sprawdza, czy dany wpis jest w ulubionych zalogowanej osoby.
        favorite_subquery = FavoritePost.objects.filter(
            user=request.user,
            post=OuterRef('pk'),
        )
        # Ulubione wpisy trafiają wyżej, a w każdej grupie działa sortowanie po dacie.
        posts = posts.annotate(is_favorite=Exists(favorite_subquery)).order_by('-is_favorite', '-date')
    else:
        # Dla gościa wystarczy zwykłe sortowanie od najnowszych wpisów.
        posts = posts.order_by('-date')

    # Do szablonu przekazujemy wpisy, listę kategorii i aktualny filtr.
    context = {
        'posts': posts,
        'categories': Post.CATEGORY_CHOICES,
        'active_category': category,
        'search_query': query,
        'random_post': random_post,
    }
    return render(request, 'posts/katalog_list.html', context)


# Widok szczegółów pokazuje jeden wpis z katalogu na podstawie jego slugu.
def post_page(request, slug):
    post = get_object_or_404(Post, slug=slug)
    is_favorite = False
    if request.user.is_authenticated:
        # Zalogowany użytkownik dostaje informację, czy wpis jest już w ulubionych.
        is_favorite = FavoritePost.objects.filter(user=request.user, post=post).exists()
    return render(request, 'posts/katalog_page.html', {'post': post, 'is_favorite': is_favorite})

@login_required(login_url="/login")
def post_new(request):
    # Dla metody POST budujemy formularz z danymi tekstowymi i ewentualnym plikiem.
    if request.method == 'POST': 
        form = forms.CreatePost(request.POST, request.FILES) 
        if form.is_valid():
            try:
                # Wspólna funkcja zapisuje wpis i przypisuje aktualnego autora.
                newpost = _save_post_from_form(form, request.user)
                return redirect('posts:list')
            except ValueError as error:
                # Zamiast błędu 500 pokazujemy prosty komunikat przy problemie z uploadem.
                if "api_secret" in str(error).lower():
                    form.add_error(
                        "banner",
                        "Nie udalo sie wyslac obrazka do Cloudinary. Sprawdz konfiguracje CLOUDINARY_API_SECRET.",
                    )
                else:
                    raise
    else:
        # Przy pierwszym wejściu pokazujemy pusty formularz dodawania.
        form = forms.CreatePost()
    return render(
        request,
        'posts/katalog_new.html',
        {
            # Ten sam szablon obsługuje dodawanie i edycję dzięki zmiennym kontekstowym.
            'form': form,
            'page_title': 'Dodaj do katalogu',
            'page_description': 'Uzupełnij kategorię, tytuł, tag i pozostałe cechy wpisu.',
            'submit_label': 'Zapisz w katalogu',
        },
    )


@login_required(login_url="/login")
def post_edit(request, slug):
    # Edytować wpis może tylko jego autor.
    post = get_object_or_404(Post, slug=slug, author=request.user)

    if request.method == 'POST':
        # Do edycji przekazujemy też `instance=post`, żeby zmienić istniejący rekord.
        form = forms.CreatePost(request.POST, request.FILES, instance=post)
        if form.is_valid():
            try:
                # Zapis przechodzi przez tę samą funkcję pomocniczą co przy dodawaniu.
                updated_post = _save_post_from_form(form, request.user)
                return redirect('posts:page', slug=updated_post.slug)
            except ValueError as error:
                # Tutaj łapiemy ten sam problem z konfiguracją Cloudinary co wyżej.
                if "api_secret" in str(error).lower():
                    form.add_error(
                        "banner",
                        "Nie udalo sie wyslac obrazka do Cloudinary. Sprawdz konfiguracje CLOUDINARY_API_SECRET.",
                    )
                else:
                    raise
    else:
        # Przy wejściu na stronę edycji formularz jest wypełniony danymi istniejącego wpisu.
        form = forms.CreatePost(instance=post)

    return render(
        request,
        'posts/katalog_new.html',
        {
            # Szablon dostaje wpis i własne opisy, żeby działał jak ekran edycji.
            'form': form,
            'post': post,
            'page_title': 'Edytuj wpis w katalogu',
            'page_description': 'Możesz poprawić tytuł, tagi, opis i pozostałe cechy swojego wpisu.',
            'submit_label': 'Zapisz zmiany',
        },
    )


@login_required(login_url="/login")
def post_delete(request, slug):
    # Usunąć wpis może tylko jego autor.
    post = get_object_or_404(Post, slug=slug, author=request.user)

    # Usuwanie wykonujemy tylko po świadomym wysłaniu formularza metodą POST.
    if request.method != 'POST':
        return redirect('posts:page', slug=post.slug)

    post.delete()
    return redirect('posts:list')


@login_required(login_url="/login")
def toggle_favorite(request, slug):
    # Dodawanie do ulubionych działa tylko po wysłaniu formularza metodą POST.
    if request.method != 'POST':
        return redirect('posts:page', slug=slug)

    post = get_object_or_404(Post, slug=slug)
    # `get_or_create` zwraca istniejące polubienie albo tworzy nowe.
    favorite, created = FavoritePost.objects.get_or_create(user=request.user, post=post)
    if not created:
        # Jeśli wpis był już w ulubionych, kliknięcie usuwa polubienie.
        favorite.delete()

    # `next` pozwala wrócić użytkownika tam, skąd wysłał formularz.
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('posts:page', slug=slug)
