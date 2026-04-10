from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from forum.models import ForumPost
from katalog.models import FavoritePost, Post
from .models import FriendRequest, Profile


# Ten test sprawdza prosty ranking oparty na aktywności społeczności.
class RecommendationsViewTests(TestCase):
    def setUp(self):
        # Tworzymy autora, użytkowników i dwa wpisy do porównania.
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

        # Pierwszy wpis dostaje więcej aktywności w ulubionych niż drugi.
        FavoritePost.objects.create(user=self.author, post=self.first_post)
        FavoritePost.objects.create(user=self.user_two, post=self.first_post)
        FavoritePost.objects.create(user=self.user_three, post=self.second_post)

        # Dodatkowe tematy forum jeszcze bardziej podbijają wynik pierwszego wpisu.
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
        # Otwieramy stronę polecajek i pobieramy listę wpisów z kontekstu.
        response = self.client.get(reverse("recommendations"))

        recommended_posts = list(response.context["recommended_posts"])

        # Spider-Man powinien być pierwszy, bo ma najwyższą sumę ulubionych i tematów forum.
        self.assertEqual(recommended_posts[0], self.first_post)
        self.assertEqual(recommended_posts[0].favorites_count, 2)
        self.assertEqual(recommended_posts[0].forum_topics_count, 2)
        self.assertEqual(recommended_posts[0].recommendation_score, 4)
        self.assertEqual(recommended_posts[1], self.second_post)


class FriendSystemTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='martina', password='tajnehaslo123')
        self.user_b = User.objects.create_user(username='anna', password='innehaslo123')

    def test_send_friend_request_and_accept(self):
        self.client.login(username='martina', password='tajnehaslo123')
        response = self.client.post(reverse('send_friend_request', args=[self.user_b.pk]), follow=True)
        self.assertTrue(FriendRequest.objects.filter(from_user=self.user_a, to_user=self.user_b).exists())

        self.client.logout()
        self.client.login(username='anna', password='innehaslo123')
        friend_request = FriendRequest.objects.get(from_user=self.user_a, to_user=self.user_b)
        response = self.client.post(reverse('accept_friend_request', args=[friend_request.pk]), follow=True)

        self.assertFalse(FriendRequest.objects.filter(pk=friend_request.pk).exists())
        self.assertIn(self.user_b.profile, self.user_a.profile.friends.all())
        self.assertIn(self.user_a.profile, self.user_b.profile.friends.all())

    def test_cancel_friend_request(self):
        self.client.login(username='martina', password='tajnehaslo123')
        self.client.post(reverse('send_friend_request', args=[self.user_b.pk]))
        self.assertTrue(FriendRequest.objects.filter(from_user=self.user_a, to_user=self.user_b).exists())

        response = self.client.post(reverse('cancel_friend_request', args=[self.user_b.pk]), follow=True)
        self.assertFalse(FriendRequest.objects.filter(from_user=self.user_a, to_user=self.user_b).exists())
