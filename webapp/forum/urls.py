from django.urls import path
from . import views

# `app_name` pozwala odwoływać się do URL-i jako `forum:index`, `forum:detail` itd.
app_name = 'forum'

urlpatterns = [
    # Strona główna forum z listą wszystkich tematów.
    path('', views.index, name='index'),
    # Formularz do dodawania nowego tematu.
    path('new-post/', views.post_new, name='new-post'),
    # Usuwanie posta forum przez jego autora.
    path('post/<int:post_id>/delete/', views.post_delete, name='delete-post'),
    # Widok pojedynczego posta na podstawie jego identyfikatora.
    path('post/<int:post_id>/', views.post_detail, name='detail'),
]
