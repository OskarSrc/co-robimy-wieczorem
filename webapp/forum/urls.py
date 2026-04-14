from django.urls import path
from . import views

# `app_name` pozwala odwoływać się do URL-i jako `forum:index`, `forum:detail` itd.
app_name = 'forum'

urlpatterns = [
    # Strona główna forum z listą wszystkich tematów.
    path('', views.index, name='index'),
    # Formularz do dodawania nowego tematu.
    path('new-post/', views.post_new, name='new-post'),
    # Widok pojedynczego posta na podstawie jego identyfikatora.
    path('post/<int:post_id>/', views.post_detail, name='detail'),
    # Edycja posta forum przez jego autora.
    path('post/<int:post_id>/edit/', views.post_edit, name='edit-post'),
    # Usuwanie posta forum przez jego autora.
    path('post/<int:post_id>/delete/', views.post_delete, name='delete-post'),
    # Dodawanie odpowiedzi do posta.
    path('post/<int:post_id>/reply/', views.reply_new, name='new-reply'),
    # Edycja odpowiedzi.
    path('reply/<int:reply_id>/edit/', views.reply_edit, name='edit-reply'),
    # Usuwanie odpowiedzi.
    path('reply/<int:reply_id>/delete/', views.reply_delete, name='delete-reply'),
]
