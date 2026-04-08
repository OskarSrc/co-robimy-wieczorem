from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from katalog.models import Post

from .models import ForumPost


# Ten zestaw testów sprawdza, czy usuwać temat forum może tylko jego autor.
class ForumDeleteViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="martina", password="tajnehaslo123")
        self.other_user = User.objects.create_user(username="anna", password="innehaslo123")
        self.catalog_post = Post.objects.create(
            category="film",
            title="Interstellar",
            body="Film science fiction.",
            author=self.author,
        )
        self.forum_post = ForumPost.objects.create(
            catalog_post=self.catalog_post,
            subject="Czy warto obejrzeć jeszcze raz?",
            body="Chcę wrócić do tego filmu w weekend.",
            author=self.author,
        )

    def test_author_can_delete_own_forum_post(self):
        self.client.login(username="martina", password="tajnehaslo123")

        response = self.client.post(
            reverse("forum:delete-post", kwargs={"post_id": self.forum_post.pk})
        )

        self.assertRedirects(response, reverse("forum:index"))
        self.assertFalse(ForumPost.objects.filter(pk=self.forum_post.pk).exists())

    def test_non_author_cannot_delete_forum_post(self):
        self.client.login(username="anna", password="innehaslo123")

        response = self.client.post(
            reverse("forum:delete-post", kwargs={"post_id": self.forum_post.pk})
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(ForumPost.objects.filter(pk=self.forum_post.pk).exists())

    def test_detail_page_shows_delete_button_only_for_author(self):
        self.client.login(username="martina", password="tajnehaslo123")
        author_response = self.client.get(
            reverse("forum:detail", kwargs={"post_id": self.forum_post.pk})
        )

        self.assertContains(
            author_response,
            reverse("forum:delete-post", kwargs={"post_id": self.forum_post.pk}),
        )

        self.client.logout()
        self.client.login(username="anna", password="innehaslo123")
        other_response = self.client.get(
            reverse("forum:detail", kwargs={"post_id": self.forum_post.pk})
        )

        self.assertNotContains(
            other_response,
            reverse("forum:delete-post", kwargs={"post_id": self.forum_post.pk}),
        )
