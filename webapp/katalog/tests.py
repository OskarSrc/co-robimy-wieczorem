from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from forum.models import ForumPost

from .models import CatalogTag, FavoritePost, Post


class CatalogViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="marty", password="pass12345")
        self.other_user = User.objects.create_user(username="ania", password="pass12345")

        self.film_tag, _ = CatalogTag.objects.get_or_create(
            slug="film-na-randke",
            defaults={"name": "Na randkę", "scope": "film", "sort_order": 1},
        )
        self.serial_tag, _ = CatalogTag.objects.get_or_create(
            slug="serial-do-binge",
            defaults={"name": "Do binge", "scope": "serial", "sort_order": 1},
        )
        self.game_tag, _ = CatalogTag.objects.get_or_create(
            slug="gra-lokalnie",
            defaults={"name": "Lokalnie", "scope": "gra", "sort_order": 1},
        )
        self.activity_tag, _ = CatalogTag.objects.get_or_create(
            slug="aktywnosci-spacer",
            defaults={"name": "Spacer", "scope": "aktywnosci", "sort_order": 1},
        )
        self.shared_group_tag, _ = CatalogTag.objects.get_or_create(
            slug="z-ekipa",
            defaults={"name": "Z ekipą", "scope": "shared", "sort_order": 2},
        )
        self.shared_city_tag, _ = CatalogTag.objects.get_or_create(
            slug="na-miescie",
            defaults={"name": "Na mieście", "scope": "shared", "sort_order": 3},
        )

        self.romantic_post = Post.objects.create(
            category="film",
            subcategory="fabularny",
            title="Wieczor na dwoje",
            body="Filmowy plan na spokojny wieczor.",
            vibe="romantycznie",
            duration_minutes=120,
            cost_level="medium",
            group_size="duo",
            weather_fit="rain",
            setting="outside",
            pick_reason="Dobry, gdy chcecie zrobic z wieczoru maly plan.",
            author=self.user,
        )
        self.romantic_post.tags.add(self.film_tag)

        self.group_post = Post.objects.create(
            category="gra",
            subcategory="planszowa",
            title="Planszowki z ekipa",
            body="Szybka gra na deszczowy wieczor.",
            vibe="ekipa",
            duration_minutes=60,
            cost_level="cheap",
            group_size="group",
            weather_fit="rain",
            setting="outside",
            pick_reason="Dobre, gdy chcecie zaczac bez duzego przygotowania.",
            author=self.user,
        )
        self.group_post.tags.add(self.shared_group_tag, self.shared_city_tag, self.game_tag)

        self.serial_post = Post.objects.create(
            category="serial",
            subcategory="miniserial",
            title="Weekendowy serial",
            body="Serial na dwa wieczory i szybkie wciągnięcie się w historię.",
            vibe="spokojny",
            duration_minutes=50,
            season_count=2,
            cost_level="cheap",
            group_size="duo",
            weather_fit="rain",
            setting="home",
            pick_reason="Dobre, gdy chcecie wejść w historię bez wielosezonowego zobowiązania.",
            author=self.user,
        )
        self.serial_post.tags.add(self.serial_tag)

        self.activity_post = Post.objects.create(
            category="aktywnosci",
            subcategory="plenerowa",
            title="Spacer o zachodzie",
            body="Lekki plan na wyjście do parku, kiedy chcecie po prostu pobyć razem.",
            vibe="romantycznie",
            duration_minutes=90,
            cost_level="free",
            group_size="duo",
            weather_fit="sun",
            setting="outside",
            pick_reason="Dobre, gdy macie ochotę wyjść z domu bez dużych przygotowań.",
            author=self.user,
        )
        self.activity_post.tags.add(self.activity_tag)

        FavoritePost.objects.create(user=self.user, post=self.group_post)
        FavoritePost.objects.create(user=self.other_user, post=self.group_post)
        ForumPost.objects.create(
            catalog_post=self.group_post,
            subject="Gramy dzisiaj?",
            body="Mozemy zaczac od razu wieczorem.",
            author=self.other_user,
        )

    def test_catalog_filters_use_selected_tag(self):
        response = self.client.get(
            reverse("posts:list"),
            {"tag": "z-ekipa"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual([post.pk for post in response.context["posts"]], [self.group_post.pk])
        self.assertEqual(response.context["results_count"], 1)

    def test_catalog_card_shows_community_signals(self):
        response = self.client.get(
            reverse("posts:list"),
            {"tag": "z-ekipa"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dodane przez marty")
        self.assertContains(response, "2 osoby zapisały")
        self.assertContains(response, "1 wątek na forum")

    def test_catalog_search_matches_post_title(self):
        response = self.client.get(
            reverse("posts:list"),
            {"q": "Weekendowy"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual([post.pk for post in response.context["posts"]], [self.serial_post.pk])
        self.assertEqual(response.context["results_count"], 1)

    def test_catalog_search_matches_tag_slug(self):
        response = self.client.get(
            reverse("posts:list"),
            {"q": "randke"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual([post.pk for post in response.context["posts"]], [self.romantic_post.pk])
        self.assertEqual(response.context["results_count"], 1)

    def test_random_pick_respects_active_filters(self):
        response = self.client.get(
            reverse("posts:list"),
            {"tag": "film-na-randke", "random": "1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["random_pick"].pk, self.romantic_post.pk)

    def test_post_page_shows_community_signals(self):
        response = self.client.get(reverse("posts:page", args=[self.group_post.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2 osoby zapisały")
        self.assertContains(response, "1 wątek na forum")

    def test_new_post_page_contains_live_preview(self):
        self.client.login(username="marty", password="pass12345")

        response = self.client.get(reverse("posts:new-post"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tak mniej więcej wpis pokaże się w katalogu.")
        self.assertContains(response, 'data-preview-card')

    def test_author_can_edit_own_film_post(self):
        self.client.login(username="marty", password="pass12345")

        response = self.client.post(
            reverse("posts:edit", args=[self.romantic_post.slug]),
            {
                "category": "film",
                "subcategory": "dokument",
                "title": "Wieczor na dwoje po zmianach",
                "body": self.romantic_post.body,
                "tags": [self.film_tag.pk],
                "pick_reason": self.romantic_post.pick_reason,
            },
        )

        self.assertRedirects(response, reverse("posts:page", args=[self.romantic_post.slug]))
        self.romantic_post.refresh_from_db()
        self.assertEqual(self.romantic_post.title, "Wieczor na dwoje po zmianach")
        self.assertEqual(self.romantic_post.subcategory, "dokument")

    def test_film_post_requires_subcategory(self):
        self.client.login(username="marty", password="pass12345")

        response = self.client.post(
            reverse("posts:edit", args=[self.romantic_post.slug]),
            {
                "category": "film",
                "subcategory": "",
                "title": self.romantic_post.title,
                "body": self.romantic_post.body,
                "tags": [self.film_tag.pk],
                "pick_reason": self.romantic_post.pick_reason,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wybierz podkategorię filmu.")

    def test_author_can_edit_own_serial_post(self):
        self.client.login(username="marty", password="pass12345")

        response = self.client.post(
            reverse("posts:edit", args=[self.serial_post.slug]),
            {
                "category": "serial",
                "subcategory": "sitcom",
                "title": "Weekendowy serial po zmianach",
                "body": self.serial_post.body,
                "tags": [self.serial_tag.pk],
                "pick_reason": self.serial_post.pick_reason,
            },
        )

        self.assertRedirects(response, reverse("posts:page", args=[self.serial_post.slug]))
        self.serial_post.refresh_from_db()
        self.assertEqual(self.serial_post.title, "Weekendowy serial po zmianach")
        self.assertEqual(self.serial_post.subcategory, "sitcom")

    def test_serial_post_requires_subcategory(self):
        self.client.login(username="marty", password="pass12345")

        response = self.client.post(
            reverse("posts:edit", args=[self.serial_post.slug]),
            {
                "category": "serial",
                "subcategory": "",
                "title": self.serial_post.title,
                "body": self.serial_post.body,
                "tags": [self.serial_tag.pk],
                "pick_reason": self.serial_post.pick_reason,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wybierz podkategorię serialu.")

    def test_serial_post_rejects_film_tags(self):
        self.client.login(username="marty", password="pass12345")

        response = self.client.post(
            reverse("posts:edit", args=[self.serial_post.slug]),
            {
                "category": "serial",
                "subcategory": "sitcom",
                "title": self.serial_post.title,
                "body": self.serial_post.body,
                "tags": [self.film_tag.pk],
                "pick_reason": self.serial_post.pick_reason,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wybrane tagi nie pasują do tej kategorii.")

    def test_author_can_edit_own_game_post(self):
        self.client.login(username="marty", password="pass12345")

        response = self.client.post(
            reverse("posts:edit", args=[self.group_post.slug]),
            {
                "category": "gra",
                "subcategory": "kooperacyjna",
                "title": "Planszowki z ekipa po zmianach",
                "body": self.group_post.body,
                "tags": [self.game_tag.pk, self.shared_group_tag.pk],
                "pick_reason": self.group_post.pick_reason,
            },
        )

        self.assertRedirects(response, reverse("posts:page", args=[self.group_post.slug]))
        self.group_post.refresh_from_db()
        self.assertEqual(self.group_post.title, "Planszowki z ekipa po zmianach")
        self.assertEqual(self.group_post.subcategory, "kooperacyjna")

    def test_game_post_requires_subcategory(self):
        self.client.login(username="marty", password="pass12345")

        response = self.client.post(
            reverse("posts:edit", args=[self.group_post.slug]),
            {
                "category": "gra",
                "subcategory": "",
                "title": self.group_post.title,
                "body": self.group_post.body,
                "tags": [self.game_tag.pk],
                "pick_reason": self.group_post.pick_reason,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wybierz podkategorię gry.")

    def test_game_post_rejects_serial_tags(self):
        self.client.login(username="marty", password="pass12345")

        response = self.client.post(
            reverse("posts:edit", args=[self.group_post.slug]),
            {
                "category": "gra",
                "subcategory": "planszowa",
                "title": self.group_post.title,
                "body": self.group_post.body,
                "tags": [self.serial_tag.pk],
                "pick_reason": self.group_post.pick_reason,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wybrane tagi nie pasują do tej kategorii.")

    def test_author_can_edit_own_activity_post(self):
        self.client.login(username="marty", password="pass12345")

        response = self.client.post(
            reverse("posts:edit", args=[self.activity_post.slug]),
            {
                "category": "aktywnosci",
                "subcategory": "kulturalna",
                "title": "Spacer o zachodzie po zmianach",
                "body": self.activity_post.body,
                "tags": [self.activity_tag.pk, self.shared_city_tag.pk],
                "pick_reason": self.activity_post.pick_reason,
            },
        )

        self.assertRedirects(response, reverse("posts:page", args=[self.activity_post.slug]))
        self.activity_post.refresh_from_db()
        self.assertEqual(self.activity_post.title, "Spacer o zachodzie po zmianach")
        self.assertEqual(self.activity_post.subcategory, "kulturalna")

    def test_activity_post_requires_subcategory(self):
        self.client.login(username="marty", password="pass12345")

        response = self.client.post(
            reverse("posts:edit", args=[self.activity_post.slug]),
            {
                "category": "aktywnosci",
                "subcategory": "",
                "title": self.activity_post.title,
                "body": self.activity_post.body,
                "tags": [self.activity_tag.pk],
                "pick_reason": self.activity_post.pick_reason,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wybierz podkategorię aktywności.")

    def test_activity_post_rejects_game_tags(self):
        self.client.login(username="marty", password="pass12345")

        response = self.client.post(
            reverse("posts:edit", args=[self.activity_post.slug]),
            {
                "category": "aktywnosci",
                "subcategory": "plenerowa",
                "title": self.activity_post.title,
                "body": self.activity_post.body,
                "tags": [self.game_tag.pk],
                "pick_reason": self.activity_post.pick_reason,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wybrane tagi nie pasują do tej kategorii.")

    def test_non_author_cannot_edit_post(self):
        self.client.login(username="ania", password="pass12345")

        response = self.client.get(reverse("posts:edit", args=[self.romantic_post.slug]))

        self.assertEqual(response.status_code, 404)

    def test_theme_page_shows_matching_posts(self):
        response = self.client.get(reverse("posts:theme", args=["top-na-randke"]))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.romantic_post, response.context["posts"])
        self.assertNotIn(self.group_post, response.context["posts"])
