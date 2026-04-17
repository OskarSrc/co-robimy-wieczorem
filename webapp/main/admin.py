from django.contrib import admin
from .models import Club, Profile, FriendRequest, VotingRoom, VotingRoomItem, VotingVote

# W panelu admina na ten moment najczęściej przydaje się zarządzanie klubami,
# dlatego niżej jest ich własna konfiguracja listy.
class ClubAdmin(admin.ModelAdmin):
    # Pokazujemy najważniejsze pola rozpoznawcze, żeby klub dało się szybko znaleźć.
    list_display = ('name', 'color', 'icon')
    filter_horizontal = ('posts',)

admin.site.register(Club, ClubAdmin)
