from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.posts_list, name="list"),
    path("new-post/", views.post_new, name="new-post"),
    path("temat/<slug:theme_slug>/", views.theme_page, name="theme"),
    path("<slug:slug>/edit/", views.post_edit, name="edit"),
    path("<slug:slug>/favorite/", views.toggle_favorite, name="favorite"),
    path("<slug:slug>", views.post_page, name="page"),
]
