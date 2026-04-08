from django.urls import path
from . import views

# `app_name` pozwala odwoływać się do adresów jako `posts:list`, `posts:page` itd.
app_name = 'posts'

urlpatterns = [
    # Główna lista wpisów w katalogu.
    path('', views.posts_list, name="list"),
    # Formularz dodawania nowej pozycji do katalogu.
    path('new-post/', views.post_new, name="new-post"),
    # Strona edycji konkretnego wpisu.
    path('<slug:slug>/edit/', views.post_edit, name="edit-post"),
    # Usuwanie wpisu z katalogu przez jego autora.
    path('<slug:slug>/delete/', views.post_delete, name="delete-post"),
    # Akcja dodawania lub usuwania wpisu z ulubionych.
    path('<slug:slug>/favorite/', views.toggle_favorite, name="favorite"),
    # Strona szczegółów pojedynczego wpisu.
    path('<slug:slug>', views.post_page, name="page"),
]
