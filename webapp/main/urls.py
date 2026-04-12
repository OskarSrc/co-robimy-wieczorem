# Plik do zarządzania ścieżkami w aplikacji. Zawiera listę ścieżek powiązanych z widokami.

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about', views.about, name='about'),
    path('cars', views.cars, name='cars'),
    path('events', views.widok_eventow, name='events'),
    path('pokoje-glosowan/', views.voting_rooms, name='voting_rooms'),
    path('pokoje-glosowan/nowy/', views.voting_room_new, name='voting_room_new'),
    path('pokoje-glosowan/<int:room_id>/', views.voting_room_detail, name='voting_room_detail'),
    path('pokoje-glosowan/<int:room_id>/glosuj/', views.submit_room_vote, name='submit_room_vote'),
    path('spolecznosc/', views.community, name='community'),
    path('spolecznosc/polecajki/', views.recommendations, name='recommendations'),
    path('spolecznosc/kluby/', views.clubs, name='clubs'),
    path('profile', views.profile_user, name='profile_user'),
    path('friends/', views.friends_list, name='friends_list'),
    path('friends/send/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friends/cancel/<int:user_id>/', views.cancel_friend_request, name='cancel_friend_request'),
    path('friends/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friends/decline/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('friends/remove/<int:user_id>/', views.remove_friend, name='remove_friend'),
    path('login', views.login_user, name='login_user'),
    path('register', views.register, name='register_user'),
    path('logout', views.logout_user, name='logout_user'),
    path('delete_account', views.delete_account, name='delete_account')
]
