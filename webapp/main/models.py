from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from katalog.models import Post

# Modele z `main` zbierają dwie większe rzeczy:
# warstwę społecznościową (profil, znajomi, kluby)
# oraz mechanikę prywatnych pokoi głosowań.

# Kluby tematyczne widoczne w sekcji community.
class Club(models.Model):
    # Klub ma prosty zestaw pól: nazwę, opis, kolor i emoji do oznaczenia członków.
    name = models.CharField(max_length=100)
    description = models.TextField()
    color = models.CharField(max_length=7, default='#6366f1')
    icon = models.CharField(max_length=50, default='')
    posts = models.ManyToManyField(Post, blank=True, related_name='clubs')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# Profil użytkownika i relacje znajomych.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=40, blank=True, null=True)
    friends = models.ManyToManyField('self', blank=True)
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')

    def __str__(self):
        return f"Profil {self.user.username}"

    def friend_usernames(self):
        return ", ".join([friend.user.username for friend in self.friends.all()])


# Zaproszenia do znajomych trzymamy osobno, żeby mieć etap "oczekuje" przed akceptacją.
class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_friend_requests',
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_friend_requests',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}"

    def accept(self):
        # Po akceptacji dokładamy profile do relacji znajomych i usuwamy samo zaproszenie.
        from_profile, _ = Profile.objects.get_or_create(user=self.from_user)
        to_profile, _ = Profile.objects.get_or_create(user=self.to_user)
        from_profile.friends.add(to_profile)
        self.delete()


# Modele odpowiedzialne za tworzenie i zamykanie pokoi głosowań.
class VotingRoom(models.Model):
    name = models.CharField(max_length=80)
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_voting_rooms',
    )
    participants = models.ManyToManyField(User, related_name='voting_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    closes_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def participants_count(self):
        return self.participants.count()

    def votes_count(self):
        return self.votes.count()

    def is_finished(self):
        # Pokój kończy się po czasie albo wtedy, gdy każdy uczestnik odda już swój głos.
        if timezone.now() >= self.closes_at:
            return True
        if not self.participants.exists():
            return False
        return self.votes.count() >= self.participants.count()


class VotingRoomItem(models.Model):
    # To pojedyncza pozycja z katalogu wrzucona do konkretnego pokoju.
    room = models.ForeignKey(
        VotingRoom,
        on_delete=models.CASCADE,
        related_name='room_items',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='voting_room_items',
    )

    class Meta:
        unique_together = ('room', 'post')
        ordering = ['id']

    def __str__(self):
        return f"{self.room.name} - {self.post.title}"


class VotingVote(models.Model):
    # Głos wskazuje jednego uczestnika i jedną pozycję z wybranego pokoju.
    room = models.ForeignKey(
        VotingRoom,
        on_delete=models.CASCADE,
        related_name='votes',
    )
    room_item = models.ForeignKey(
        VotingRoomItem,
        on_delete=models.CASCADE,
        related_name='votes',
    )
    voter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='voting_votes',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('room', 'voter')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.voter.username} -> {self.room_item.post.title}"

    def clean(self):
        # Walidacja pilnuje, żeby nie dało się zagłosować na pozycję z innego pokoju.
        if self.room_item.room_id != self.room_id:
            raise ValidationError("Glos musi wskazywac pozycje z tego samego pokoju.")
        # Dodatkowo głosować może tylko osoba faktycznie dopisana do uczestników.
        if not self.room.participants.filter(pk=self.voter_id).exists():
            raise ValidationError("Glosowac moga tylko uczestnicy pokoju.")

    def save(self, *args, **kwargs):
        # Zapis zawsze przechodzi przez `clean()`, żeby ta zasada działała też poza formularzem.
        self.clean()
        super().save(*args, **kwargs)
