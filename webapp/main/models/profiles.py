from django.contrib.auth.models import User
from django.db import models

from .clubs import Club


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=40, blank=True, null=True)
    friends = models.ManyToManyField("self", blank=True)
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True, related_name="members")

    def __str__(self):
        return f"Profil {self.user.username}"

    def friend_usernames(self):
        return ", ".join([friend.user.username for friend in self.friends.all()])


class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_friend_requests",
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_friend_requests",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("from_user", "to_user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}"

    def accept(self):
        from_profile, _ = Profile.objects.get_or_create(user=self.from_user)
        to_profile, _ = Profile.objects.get_or_create(user=self.to_user)
        from_profile.friends.add(to_profile)
        self.delete()