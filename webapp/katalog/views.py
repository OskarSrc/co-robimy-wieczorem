import random
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, OuterRef, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from . import forms
from .models import CatalogTag, FavoritePost, Post


# THEME_CONFIGS opisuje "redakcyjne" skróty na stronie katalogu.
# Każdy temat ma swój tytuł, krótki opis i regułę pobierania wpisów.
THEME_CONFIGS = {
    "top-na-randke": {
        "title": "Top na randkę",
        "description": "Klimatyczne propozycje na wspólny wieczór, kiedy liczy się nastrój i trochę więcej przestrzeni dla was.",
        "teaser": "Przejdź do gotowych inspiracji na spokojniejszy, bardziej wspólny wieczór.",
        "query": Q(tags__slug__in=["film-na-randke", "aktywnosci-na-randke", "dla-dwojga"]),
        "order_by": ("-favorite_count", "-forum_count", "-date"),
    },
    "top-na-wyjscie-z-przyjaciolmi": {
        "title": "Top na wyjście z przyjaciółmi",
        "description": "Pomysły na wyjście i wspólne akcje, które najlepiej działają, gdy zbiera się ekipa.",
        "teaser": "Zobacz temat z propozycjami na wspólne wyjścia i mocniej społeczny wieczór.",
        "query": Q(tags__slug__in=["z-ekipa", "na-miescie", "gra-na-smiech", "aktywnosci-aktywnie"]),
        "order_by": ("-favorite_count", "-forum_count", "-date"),
    },
    "na-dzis": {
        "title": "Na dziś",
        "description": "Najszybszy skrót do świeżych propozycji na teraz, bez długiego zastanawiania się.",
        "teaser": "Wejdź od razu do aktualnych i najświeższych pomysłów na wieczór.",
        "query": None,
        "order_by": ("-date",),
    },
    "popularne-w-spolecznosci": {
        "title": "Popularne w społeczności",
        "description": "To, co ludzie najczęściej zapisują, polecają i podają dalej w rozmowach.",
        "teaser": "Podejrzyj temat z propozycjami, które już łapią uwagę społeczności.",
        "query": None,
        "order_by": ("-favorite_count", "-forum_count", "-date"),
    },
}


# Helpery poniżej spinają listę katalogu, tematy i formularz,
# żeby te same reguły nie były powielane w kilku widokach.
def _annotate_posts(posts, user):
    # Te zliczenia i flagi trzymamy w jednym miejscu,
    # bo korzysta z nich lista katalogu, tematy i szczegół wpisu.
    posts = posts.select_related("author").prefetch_related("tags").annotate(
        favorite_count=Count("favorited_by", distinct=True),
        forum_count=Count("forum_posts", distinct=True),
    )

    if user.is_authenticated:
        favorite_subquery = FavoritePost.objects.filter(
            user=user,
            post=OuterRef("pk"),
        )
        posts = posts.annotate(is_favorite=Exists(favorite_subquery))

    return posts


def _theme_config(theme_slug):
    # Ten helper tylko pilnuje, żebyśmy zawsze pracowali
    # na poprawnej konfiguracji tematu, a nie na "gołym" stringu ze ścieżki.
    config = THEME_CONFIGS.get(theme_slug)
    if not config:
        raise Http404("Nie ma takiego tematu katalogu.")
    return config


def _theme_queryset(posts, theme_slug):
    # Tutaj dzieje się właściwe filtrowanie tematu.
    # Jeśli temat ma query, zawężamy wpisy. Jeśli nie ma,
    # temat działa bardziej jak gotowy sposób sortowania.
    config = _theme_config(theme_slug)
    themed_posts = posts
    if config["query"] is not None:
        themed_posts = themed_posts.filter(config["query"]).distinct()
    return themed_posts.order_by(*config["order_by"])


def _theme_cards(posts):
    # Karty tematów liczymy z jednego źródła,
    # żeby skróty na stronie głównej nie rozjeżdżały się z realnymi wynikami.
    cards = []
    for slug, config in THEME_CONFIGS.items():
        themed_posts = _theme_queryset(posts, slug)
        cards.append(
            {
                "slug": slug,
                "title": config["title"],
                "description": config["teaser"],
                "count": themed_posts.count(),
            }
        )
    return cards


def _subcategory_configs():
    # JS dostaje tylko to, czego potrzebuje do przełączania formularza,
    # bez wyciągania całej konfiguracji modelu do szablonu.
    return {
        category: {
            "label": config["subcategory_label"],
            "options": [{"value": value, "label": label} for value, label in config["choices"]],
        }
        for category, config in Post.CATEGORY_DETAIL_CONFIG.items()
    }


def _category_tag_groups():
    # Tagi grupujemy po kategorii już tutaj,
    # żeby szablon tylko je wyświetlał, a nie składał reguły po swojemu.
    return [
        {
            "category": category,
            "title": Post.category_tag_group_label(category),
            "tags": CatalogTag.objects.filter(scope=Post.category_specific_tag_scope(category)).order_by(
                "sort_order", "name"
            ),
        }
        for category in Post.CATEGORY_DETAIL_CONFIG
    ]


def _form_context(form, action_url, page_heading, page_copy, submit_label):
    selected_values = form["tags"].value() or []
    selected_category = (
        form.data.get("category")
        or form.initial.get("category")
        or getattr(form.instance, "category", "")
        or "film"
    )
    selected_subcategory_choices = Post.subcategory_choices(selected_category)

    # Nowy wpis i edycja korzystają z tego samego kontekstu,
    # żeby formularz i preview zachowywały się identycznie w obu miejscach.
    # To też upraszcza utrzymanie: gdy zmieniamy układ formularza,
    # poprawiamy go w jednym miejscu zamiast w dwóch widokach.
    return {
        "form": form,
        "form_action": action_url,
        "page_heading": page_heading,
        "page_copy": page_copy,
        "submit_label": submit_label,
        "selected_category": selected_category,
        "selected_tag_values": [str(value) for value in selected_values],
        "shared_tags": CatalogTag.objects.filter(scope="shared").order_by("sort_order", "name"),
        "category_tag_groups": _category_tag_groups(),
        "subcategory_configs": _subcategory_configs(),
        "show_subcategory": bool(selected_subcategory_choices),
        "selected_subcategory_label": Post.subcategory_form_label(selected_category),
    }


def _apply_search(posts, search_query):
    # Szukamy jednocześnie po tytule i tagach,
    # bo użytkownik częściej wpisuje klimat niż dokładną nazwę pozycji.
    # Rozbijamy wyszukiwanie na słowa, żeby "film randka" nadal dawało sensowne wyniki.
    terms = [term.strip() for term in search_query.split() if term.strip()]
    for term in terms:
        slug_term = slugify(term)
        term_query = Q(title__icontains=term) | Q(tags__name__icontains=term)
        if slug_term:
            term_query |= Q(tags__slug__icontains=slug_term)
        posts = posts.filter(term_query)
    return posts.distinct()


def posts_list(request):
    category = request.GET.get("category") or ""
    tag_slug = request.GET.get("tag") or ""
    search_query = (request.GET.get("q") or "").strip()

    # Wszystkie filtry składamy na jednym querysetcie,
    # dzięki czemu wyszukiwanie, tagi i kategorie mogą działać razem.
    posts = Post.objects.all()
    if category:
        posts = posts.filter(category=category)
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug).distinct()
    if search_query:
        posts = _apply_search(posts, search_query)

    # Dopiero po filtrowaniu dokładamy adnotacje społeczne.
    # Dzięki temu liczymy ulubione i wątki tylko dla wyników,
    # które rzeczywiście są na aktualnej liście.
    posts = _annotate_posts(posts, request.user)
    if request.user.is_authenticated:
        # Zalogowany użytkownik widzi swoje ulubione wyżej,
        # ale nadal w obrębie popularnych i aktywnych propozycji.
        posts = posts.order_by("-is_favorite", "-favorite_count", "-forum_count", "-date")
    else:
        posts = posts.order_by("-favorite_count", "-forum_count", "-date")

    random_pick = None
    if request.GET.get("random") == "1":
        # Losowanie bierze już przefiltrowane wyniki,
        # więc nie wyciąga propozycji z zupełnie innego klimatu.
        post_ids = list(posts.values_list("pk", flat=True))
        if post_ids:
            random_pick = posts.filter(pk=random.choice(post_ids)).first()

    catalog_tags = CatalogTag.objects.order_by("scope", "sort_order", "name")
    active_tag = catalog_tags.filter(slug=tag_slug).first()

    # Karty tematów liczymy z pełnej bazy wpisów, a nie z już przefiltrowanej listy,
    # bo mają działać jako osobne przejścia, a nie kolejny widok tego samego filtra.
    themed_source = _annotate_posts(Post.objects.all(), request.user)

    filter_query_params = {}
    if tag_slug:
        filter_query_params["tag"] = tag_slug
    if search_query:
        filter_query_params["q"] = search_query

    context = {
        "posts": posts,
        "categories": Post.CATEGORY_CHOICES,
        "catalog_tags": catalog_tags,
        "theme_cards": _theme_cards(themed_source),
        "random_pick": random_pick,
        "active_category": category,
        "active_tag": tag_slug,
        "search_query": search_query,
        "active_category_label": dict(Post.CATEGORY_CHOICES).get(category, ""),
        "active_tag_label": active_tag.name if active_tag else "",
        "filter_query": urlencode(filter_query_params),
        "results_count": posts.count(),
        "active_filters_count": sum(1 for value in [category, tag_slug, search_query] if value),
        "has_active_filters": any([category, tag_slug, search_query]),
    }
    return render(request, "posts/katalog_list.html", context)


def theme_page(request, theme_slug):
    # Strona tematu korzysta z tych samych helperów co lista katalogu,
    # żeby sortowanie, zliczenia i logika "topów" były wszędzie spójne.
    theme = _theme_config(theme_slug)
    posts = _annotate_posts(Post.objects.all(), request.user)
    posts = _theme_queryset(posts, theme_slug)

    context = {
        "theme_slug": theme_slug,
        "theme_title": theme["title"],
        "theme_description": theme["description"],
        "posts": posts,
        "results_count": posts.count(),
    }
    return render(request, "posts/katalog_theme.html", context)


def post_page(request, slug):
    # Szczegół wpisu korzysta z tych samych adnotacji co lista,
    # żeby ulubione i sygnały społecznościowe zawsze liczyły się tak samo.
    post = get_object_or_404(_annotate_posts(Post.objects.filter(slug=slug), request.user), slug=slug)
    is_favorite = getattr(post, "is_favorite", False)
    return render(request, "posts/katalog_page.html", {"post": post, "is_favorite": is_favorite})


@login_required(login_url="/login")
def post_new(request):
    # Widok nowego wpisu opiera się na tym samym formularzu co edycja,
    # ale startuje od pustych danych i przypisuje autora dopiero przy zapisie.
    if request.method == "POST":
        form = forms.CreatePost(request.POST, request.FILES)
        if form.is_valid():
            newpost = form.save(commit=False)
            newpost.author = request.user
            newpost.save()
            form.save_m2m()
            return redirect("posts:page", slug=newpost.slug)
    else:
        form = forms.CreatePost()

    context = _form_context(
        form,
        action_url=request.path,
        page_heading="Dodaj do katalogu",
        page_copy="Uzupełnij opis i tagi, żeby inni mogli łatwiej wybrać coś na wieczór.",
        submit_label="Zapisz w katalogu",
    )
    return render(request, "posts/katalog_new.html", context)


@login_required(login_url="/login")
def post_edit(request, slug):
    # Edycję może robić tylko autor wpisu.
    # Dzięki temu nie potrzebujemy osobnej dodatkowej walidacji po zapisie.
    post = get_object_or_404(Post.objects.prefetch_related("tags"), slug=slug, author=request.user)

    if request.method == "POST":
        form = forms.CreatePost(request.POST, request.FILES, instance=post)
        if form.is_valid():
            edited_post = form.save(commit=False)
            edited_post.author = request.user
            edited_post.save()
            form.save_m2m()
            return redirect("posts:page", slug=edited_post.slug)
    else:
        form = forms.CreatePost(instance=post)

    context = _form_context(
        form,
        action_url=request.path,
        page_heading="Edytuj wpis w katalogu",
        page_copy="Popraw opis, podkategorię i tagi widoczne na karcie.",
        submit_label="Zapisz zmiany",
    )
    return render(request, "posts/katalog_new.html", context)


@login_required(login_url="/login")
def toggle_favorite(request, slug):
    if request.method != "POST":
        return redirect("posts:page", slug=slug)

    post = get_object_or_404(Post, slug=slug)
    # Ten sam endpoint obsługuje dodanie i usunięcie z ulubionych,
    # żeby przycisk na karcie nie potrzebował osobnej logiki po obu stronach.
    favorite, created = FavoritePost.objects.get_or_create(user=request.user, post=post)
    if not created:
        favorite.delete()

    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("posts:page", slug=slug)
