from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from katalog.models import Post

from .forms import CreateForumPost
from .models import ForumPost

def index(request):
    posts = ForumPost.objects.select_related("catalog_post", "author")
    return render(request, 'forum/index.html', {'posts': posts})


def post_detail(request, post_id):
    post = get_object_or_404(
        ForumPost.objects.select_related("catalog_post", "author"),
        pk=post_id,
    )
    return render(request, 'forum/post_detail.html', {'post': post})


@login_required(login_url="/login")
def post_new(request):
    initial = {}
    catalog_slug = request.GET.get("catalog")
    if catalog_slug:
        catalog_post = get_object_or_404(Post, slug=catalog_slug)
        initial["catalog_post"] = catalog_post

    if request.method == 'POST':
        form = CreateForumPost(request.POST)
        if form.is_valid():
            forum_post = form.save(commit=False)
            forum_post.author = request.user
            forum_post.save()
            return redirect('forum:detail', post_id=forum_post.pk)
    else:
        form = CreateForumPost(initial=initial)

    return render(request, 'forum/new_post.html', {'form': form})
