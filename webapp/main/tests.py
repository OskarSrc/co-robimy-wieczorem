from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from forum.models import ForumPost
from katalog.models import CatalogTag, FavoritePost, Post


class CommunityPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="marty", password="pass12345")
        self.other_user = User.objects.create_user(username="ania", password="pass12345")

        self.shared_tag = CatalogTag.objects.create(
            name="Z ekipą",
            slug="z-ekipa-main-test",
            scope="shared",
            sort_order=1,
        )

        self.post = Post.objects.create(
            category="film",
            subcategory="fabularny",
            title="Wieczór w kinowym klimacie",
            body="Spokojny film na wspólny wieczór.",
            pick_reason="Dobry wybór, kiedy chcecie wejść w klimat bez długiego szukania.",
            author=self.user,
        )
        self.post.tags.add(self.shared_tag)

        FavoritePost.objects.create(user=self.user, post=self.post)
        ForumPost.objects.create(
            catalog_post=self.post,
            subject="Czy ten film nadaje się na wspólny wieczór?",
            body="Szukam czegoś lekkiego, ale z klimatem.",
            author=self.other_user,
        )

    def test_community_page_renders_sections(self):
        response = self.client.get(reverse("community"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Co chcesz zrobić?")
        self.assertContains(response, "Teraz jest na topie")
        self.assertContains(response, "Znajdź swój klimat")
        self.assertContains(response, "Pytanie na dziś")

    def test_community_page_shows_existing_catalog_and_forum_data(self):
        response = self.client.get(reverse("community"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
        self.assertContains(response, "Czy ten film nadaje się na wspólny wieczór?")
        self.assertContains(response, self.shared_tag.name)

    def test_community_page_does_not_render_template_comments(self):
        response = self.client.get(reverse("community"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "{#")
