from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from katalog.models import Post

from .forms import CreateForumPost
from .models import ForumPost


# Widok główny pobiera wszystkie tematy forum i wyświetla je na liście.
def index(request):
    # `select_related` ogranicza liczbę zapytań do bazy dla autora i pozycji z katalogu.
    posts = ForumPost.objects.select_related("catalog_post", "author")
    return render(request, 'forum/index.html', {'posts': posts})


# Widok szczegółów pokazuje jeden konkretny temat forum.
def post_detail(request, post_id):
    # Jeśli temat nie istnieje, Django zwróci błąd 404 zamiast awarii aplikacji.
    post = get_object_or_404(
        ForumPost.objects.select_related("catalog_post", "author"),
        pk=post_id,
    )
    return render(request, 'forum/post_detail.html', {'post': post})


@login_required(login_url="/login")
def post_new(request):
    # `initial` pozwala wstępnie wypełnić formularz danymi z parametru GET.
    initial = {}
    # Z katalogu można wejść od razu do tworzenia posta dla konkretnej pozycji.
    catalog_slug = request.GET.get("catalog")
    if catalog_slug:
        # Pobieramy obiekt katalogu po `slug`, aby ustawić go jako domyślny wybór.
        catalog_post = get_object_or_404(Post, slug=catalog_slug)
        initial["catalog_post"] = catalog_post

    if request.method == 'POST':
        # Po wysłaniu formularza bierzemy dane z `request.POST`.
        form = CreateForumPost(request.POST)
        if form.is_valid():
            # `commit=False` pozwala dopisać autora przed zapisaniem rekordu.
            forum_post = form.save(commit=False)
            # Autorem zawsze jest aktualnie zalogowany użytkownik.
            forum_post.author = request.user
            # Dopiero tutaj rekord trafia do bazy danych.
            forum_post.save()
            # Po zapisie wracamy na stronę szczegółów nowego posta.
            return redirect('forum:detail', post_id=forum_post.pk)
    else:
        # Przy pierwszym wejściu pokazujemy pusty formularz lub formularz z `initial`.
        form = CreateForumPost(initial=initial)

    # Ten sam szablon obsługuje pusty formularz i formularz z błędami walidacji.
    return render(request, 'forum/new_post.html', {'form': form})


@login_required(login_url="/login")
def post_delete(request, post_id):
    # Usunąć temat może tylko jego autor.
    post = get_object_or_404(ForumPost, pk=post_id, author=request.user)

    # Usuwanie wykonujemy wyłącznie po wysłaniu formularza metodą POST.
    if request.method != 'POST':
        return redirect('forum:detail', post_id=post.pk)

    post.delete()
    return redirect('forum:index')
