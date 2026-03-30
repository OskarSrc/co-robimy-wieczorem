from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404, redirect, render

from . import forms
from .models import FavoritePost, Post
# Create your views here.


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
            newpost = form.save(commit=False) 
            newpost.author = request.user 
            newpost.save()
            return redirect('posts:list')
    else:
        form = forms.CreatePost()
    return render(request, 'posts/katalog_new.html', { 'form': form })


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
