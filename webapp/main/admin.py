from django.contrib import admin
from .models import Club, Profile, FriendRequest, VotingRoom, VotingRoomItem, VotingVote

class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'icon')
    filter_horizontal = ('posts',)

admin.site.register(Club, ClubAdmin)
