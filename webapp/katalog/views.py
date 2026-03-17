from django.shortcuts import render, redirect
from .models import Post
from django.contrib.auth.decorators import login_required
from . import forms 
# Create your views here.


def posts_list(request):
    category = request.GET.get('category')
    posts = Post.objects.all().order_by('-date')
    if category:
        posts = posts.filter(category=category)

    context = {
        'posts': posts,
        'categories': Post.CATEGORY_CHOICES,
        'active_category': category,
    }
    return render(request, 'posts/katalog_list.html', context)


def post_page(request, slug):
    post = Post.objects.get(slug=slug)
    return render(request, 'posts/katalog_page.html', {'post': post})

@login_required(login_url="/users/login/")
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
