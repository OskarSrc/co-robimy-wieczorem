from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from forum.models import ForumPost
from katalog.models import FavoritePost, Post
from .models import FriendRequest, Profile, VotingRoom, VotingRoomItem, VotingVote


class RecommendationsViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="martina", password="tajnehaslo123")
        self.user_two = User.objects.create_user(username="anna", password="innehaslo123")
        self.user_three = User.objects.create_user(username="ola", password="kolejnehaslo123")

        self.first_post = Post.objects.create(
            category="film",
            title="Spider-Man",
            body="Lekki film na wieczór.",
            author=self.author,
        )
        self.second_post = Post.objects.create(
            category="serial",
            title="Dark",
            body="Serial do dłuższego oglądania.",
            author=self.author,
        )

        FavoritePost.objects.create(user=self.author, post=self.first_post)
        FavoritePost.objects.create(user=self.user_two, post=self.first_post)
        FavoritePost.objects.create(user=self.user_three, post=self.second_post)

        ForumPost.objects.create(
            catalog_post=self.first_post,
            subject="Czy warto obejrzeć w weekend?",
            body="Chętnie poznam opinie innych.",
            author=self.author,
        )
        ForumPost.objects.create(
            catalog_post=self.first_post,
            subject="Najlepsza część Spider-Mana",
            body="Która część najbardziej Wam siadła?",
            author=self.user_two,
        )

    def test_recommendations_are_sorted_by_simple_community_score(self):
        response = self.client.get(reverse("recommendations"))
        recommended_posts = list(response.context["recommended_posts"])

        self.assertEqual(recommended_posts[0], self.first_post)
        self.assertEqual(recommended_posts[0].favorites_count, 2)
        self.assertEqual(recommended_posts[0].forum_topics_count, 2)
        self.assertEqual(recommended_posts[0].recommendation_score, 4)
        self.assertEqual(recommended_posts[1], self.second_post)


class VotingRoomsViewTests(TestCase):
    def test_voting_rooms_page_is_available(self):
        response = self.client.get(reverse('voting_rooms'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/voting_rooms/index.html')
        self.assertContains(response, 'Pokoje głosowań')

    def test_home_page_links_to_voting_rooms(self):
        response = self.client.get(reverse('home'))

        self.assertContains(response, reverse('voting_rooms'))

    def test_voting_rooms_page_links_to_separate_create_page(self):
        User.objects.create_user(username='mati', password='tajnehaslo123')
        self.client.login(username='mati', password='tajnehaslo123')

        response = self.client.get(reverse('voting_rooms'))

        self.assertContains(response, reverse('voting_room_new'))

    def test_voting_rooms_page_no_longer_shows_old_stat_boxes(self):
        response = self.client.get(reverse('voting_rooms'))

        self.assertNotContains(response, 'tylu znajomych masz już gotowych do zaproszenia')


class VotingRoomFlowTests(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username='mati', password='tajnehaslo123')
        self.friend = User.objects.create_user(username='ola', password='innehaslo123')
        self.other_user = User.objects.create_user(username='krzysiek', password='innehaslo456')

        self.creator_profile = Profile.objects.create(user=self.creator)
        self.friend_profile = Profile.objects.create(user=self.friend)
        Profile.objects.create(user=self.other_user)
        self.creator_profile.friends.add(self.friend_profile)

        self.first_post = Post.objects.create(
            category='film',
            title='Diuna',
            body='Sci-fi na wspólny wieczór.',
            author=self.creator,
        )
        self.second_post = Post.objects.create(
            category='gra',
            title='Overcooked',
            body='Gra do szybkiej współpracy.',
            author=self.creator,
        )

    def test_create_page_is_available_for_logged_user(self):
        self.client.login(username='mati', password='tajnehaslo123')

        response = self.client.get(reverse('voting_room_new'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/voting_rooms/new.html')
        self.assertContains(response, 'Utwórz pokój')

    def test_logged_user_can_create_voting_room(self):
        self.client.login(username='mati', password='tajnehaslo123')
        response = self.client.post(reverse('voting_room_new'), {
            'name': 'Piątkowy test',
            'duration_minutes': 30,
            'friends': [self.friend.id],
            'posts': [self.first_post.id, self.second_post.id],
        })

        room = VotingRoom.objects.get(name='Piątkowy test')

        self.assertRedirects(response, reverse('voting_room_detail', args=[room.id]))
        self.assertEqual(room.creator, self.creator)
        self.assertEqual(room.participants.count(), 2)
        self.assertTrue(room.participants.filter(pk=self.creator.id).exists())
        self.assertTrue(room.participants.filter(pk=self.friend.id).exists())
        self.assertEqual(room.room_items.count(), 2)

    def test_non_participant_cannot_open_room(self):
        room = VotingRoom.objects.create(
            name='Pokój prywatny',
            creator=self.creator,
            closes_at=timezone.now() + timedelta(minutes=30),
        )
        room.participants.add(self.creator, self.friend)
        VotingRoomItem.objects.create(room=room, post=self.first_post)

        self.client.login(username='krzysiek', password='innehaslo456')
        response = self.client.get(reverse('voting_room_detail', args=[room.id]))

        self.assertEqual(response.status_code, 404)

    def test_participants_can_vote_and_room_finishes_after_all_votes(self):
        room = VotingRoom.objects.create(
            name='Wieczorne głosowanie',
            creator=self.creator,
            closes_at=timezone.now() + timedelta(minutes=30),
        )
        room.participants.add(self.creator, self.friend)
        first_item = VotingRoomItem.objects.create(room=room, post=self.first_post)
        second_item = VotingRoomItem.objects.create(room=room, post=self.second_post)

        self.client.login(username='mati', password='tajnehaslo123')
        creator_response = self.client.post(reverse('submit_room_vote', args=[room.id]), {
            'room_item': first_item.id,
        })

        self.assertRedirects(creator_response, reverse('voting_room_detail', args=[room.id]))
        self.assertEqual(VotingVote.objects.filter(room=room).count(), 1)
        room.refresh_from_db()
        self.assertFalse(room.is_finished())

        self.client.logout()
        self.client.login(username='ola', password='innehaslo123')
        friend_response = self.client.post(reverse('submit_room_vote', args=[room.id]), {
            'room_item': second_item.id,
        })

        self.assertRedirects(friend_response, reverse('voting_room_detail', args=[room.id]))
        self.assertEqual(VotingVote.objects.filter(room=room).count(), 2)
        room.refresh_from_db()
        self.assertTrue(room.is_finished())

    def test_room_detail_shows_vote_result_after_finish(self):
        room = VotingRoom.objects.create(
            name='Gotowy pokój',
            creator=self.creator,
            closes_at=timezone.now() + timedelta(minutes=30),
        )
        room.participants.add(self.creator, self.friend)
        winning_item = VotingRoomItem.objects.create(room=room, post=self.first_post)
        VotingRoomItem.objects.create(room=room, post=self.second_post)
        VotingVote.objects.create(room=room, room_item=winning_item, voter=self.creator)
        VotingVote.objects.create(room=room, room_item=winning_item, voter=self.friend)

        self.client.login(username='mati', password='tajnehaslo123')
        response = self.client.get(reverse('voting_room_detail', args=[room.id]))

        self.assertContains(response, 'Gotowy pokój')
        self.assertContains(response, 'Wszyscy oddali głosy')
        self.assertContains(response, self.first_post.title)
        self.assertContains(response, '2 głosów')


class FriendSystemTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='martina', password='tajnehaslo123')
        self.user_b = User.objects.create_user(username='anna', password='innehaslo123')

    def test_send_friend_request_and_accept(self):
        self.client.login(username='martina', password='tajnehaslo123')
        self.client.post(reverse('send_friend_request', args=[self.user_b.pk]), follow=True)
        self.assertTrue(FriendRequest.objects.filter(from_user=self.user_a, to_user=self.user_b).exists())

        self.client.logout()
        self.client.login(username='anna', password='innehaslo123')
        friend_request = FriendRequest.objects.get(from_user=self.user_a, to_user=self.user_b)
        self.client.post(reverse('accept_friend_request', args=[friend_request.pk]), follow=True)

        self.assertFalse(FriendRequest.objects.filter(pk=friend_request.pk).exists())
        self.assertIn(self.user_b.profile, self.user_a.profile.friends.all())
        self.assertIn(self.user_a.profile, self.user_b.profile.friends.all())

    def test_cancel_friend_request(self):
        self.client.login(username='martina', password='tajnehaslo123')
        self.client.post(reverse('send_friend_request', args=[self.user_b.pk]))
        self.assertTrue(FriendRequest.objects.filter(from_user=self.user_a, to_user=self.user_b).exists())

        self.client.post(reverse('cancel_friend_request', args=[self.user_b.pk]), follow=True)
        self.assertFalse(FriendRequest.objects.filter(from_user=self.user_a, to_user=self.user_b).exists())
