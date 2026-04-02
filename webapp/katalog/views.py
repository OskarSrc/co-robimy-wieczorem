from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404, redirect, render

from . import forms
from .models import FavoritePost, Post
# Create your views here.


def _save_post_from_form(form, author):
    # Wspolna logika zapisu dla dodawania i edycji wpisu.
    newpost = form.save(commit=False)
    newpost.author = author
    newpost.save()
    return newpost


def posts_list(request):
    category = request.GET.get('category')
    posts = Post.objects.all()
    if category:
        posts = posts.filter(category=category)

    if request.user.is_authenticated:
        favorite_subquery = FavoritePost.objects.filter(
            user=request.user,
            post=OuterRef('pk'),
        )
        posts = posts.annotate(is_favorite=Exists(favorite_subquery)).order_by('-is_favorite', '-date')
    else:
        posts = posts.order_by('-date')

    context = {
        'posts': posts,
        'categories': Post.CATEGORY_CHOICES,
        'active_category': category,
    }
    return render(request, 'posts/katalog_list.html', context)


def post_page(request, slug):
    post = get_object_or_404(Post, slug=slug)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoritePost.objects.filter(user=request.user, post=post).exists()
    return render(request, 'posts/katalog_page.html', {'post': post, 'is_favorite': is_favorite})

@login_required(login_url="/login")
def post_new(request):
    if request.method == 'POST': 
        form = forms.CreatePost(request.POST, request.FILES) 
        if form.is_valid():
            try:
                newpost = _save_post_from_form(form, request.user)
                return redirect('posts:list')
            except ValueError as error:
                # Zamiast bledu 500 pokazujemy prosty komunikat przy problemie z uploadem.
                if "api_secret" in str(error).lower():
                    form.add_error(
                        "banner",
                        "Nie udalo sie wyslac obrazka do Cloudinary. Sprawdz konfiguracje CLOUDINARY_API_SECRET.",
                    )
                else:
                    raise
    else:
        form = forms.CreatePost()
    return render(
        request,
        'posts/katalog_new.html',
        {
            'form': form,
            'page_title': 'Dodaj do katalogu',
            'page_description': 'Uzupełnij kategorię, tytuł, tag i pozostałe cechy wpisu.',
            'submit_label': 'Zapisz w katalogu',
        },
    )


@login_required(login_url="/login")
def post_edit(request, slug):
    # Edytowac wpis moze tylko jego autor.
    post = get_object_or_404(Post, slug=slug, author=request.user)

    if request.method == 'POST':
        form = forms.CreatePost(request.POST, request.FILES, instance=post)
        if form.is_valid():
            try:
                updated_post = _save_post_from_form(form, request.user)
                return redirect('posts:page', slug=updated_post.slug)
            except ValueError as error:
                if "api_secret" in str(error).lower():
                    form.add_error(
                        "banner",
                        "Nie udalo sie wyslac obrazka do Cloudinary. Sprawdz konfiguracje CLOUDINARY_API_SECRET.",
                    )
                else:
                    raise
    else:
        form = forms.CreatePost(instance=post)

    return render(
        request,
        'posts/katalog_new.html',
        {
            'form': form,
            'post': post,
            'page_title': 'Edytuj wpis w katalogu',
            'page_description': 'Możesz poprawić tytuł, tagi, opis i pozostałe cechy swojego wpisu.',
            'submit_label': 'Zapisz zmiany',
        },
    )


@login_required(login_url="/login")
def toggle_favorite(request, slug):
    if request.method != 'POST':
        return redirect('posts:page', slug=slug)

    post = get_object_or_404(Post, slug=slug)
    favorite, created = FavoritePost.objects.get_or_create(user=request.user, post=post)
    if not created:
        favorite.delete()

    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('posts:page', slug=slug)
