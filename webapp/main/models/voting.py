from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from katalog.models import Post


class VotingRoom(models.Model):
    name = models.CharField(max_length=80)
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_voting_rooms",
    )
    participants = models.ManyToManyField(User, related_name="voting_rooms")
    created_at = models.DateTimeField(auto_now_add=True)
    closes_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def participants_count(self):
        return self.participants.count()

    def votes_count(self):
        return self.votes.count()

    def is_finished(self):
        if timezone.now() >= self.closes_at:
            return True
        if not self.participants.exists():
            return False
        return self.votes.count() >= self.participants.count()


class VotingRoomItem(models.Model):
    room = models.ForeignKey(
        VotingRoom,
        on_delete=models.CASCADE,
        related_name="room_items",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="voting_room_items",
    )

    class Meta:
        unique_together = ("room", "post")
        ordering = ["id"]

    def __str__(self):
        return f"{self.room.name} - {self.post.title}"


class VotingVote(models.Model):
    room = models.ForeignKey(
        VotingRoom,
        on_delete=models.CASCADE,
        related_name="votes",
    )
    room_item = models.ForeignKey(
        VotingRoomItem,
        on_delete=models.CASCADE,
        related_name="votes",
    )
    voter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="voting_votes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("room", "voter")
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.voter.username} -> {self.room_item.post.title}"

    def clean(self):
        if self.room_item.room_id != self.room_id:
            raise ValidationError("Glos musi wskazywac pozycje z tego samego pokoju.")
        if not self.room.participants.filter(pk=self.voter_id).exists():
            raise ValidationError("Glosowac moga tylko uczestnicy pokoju.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)