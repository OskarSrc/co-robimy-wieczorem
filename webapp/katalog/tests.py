from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import CreatePost
from .models import Post


# Ten zestaw testów sprawdza podstawowe cechy modelu i formularza katalogu.
class PostCatalogFeaturesTests(TestCase):
    def test_post_stores_simple_catalog_features(self):
        # Tworzymy przykładowy wpis z uzupełnionymi polami opisującymi propozycję.
        post = Post.objects.create(
            category="film",
            title="Attack on Titan",
            body="Anime akcji z watkiem fantasy.",
            tagi="anime",
            podtag_anime="shonen",
            okazja="solo",
            liczba_osob="1_osoba",
            cena="srednio",
        )

        # `get_*_display()` zamienia zapis techniczny na etykietę przyjazną dla użytkownika.
        self.assertEqual(post.get_tagi_display(), "Anime")
        self.assertEqual(post.get_podtag_anime_display(), "Shonen")
        self.assertEqual(post.get_okazja_display(), "Samemu (Solo)")
        self.assertEqual(post.get_liczba_osob_display(), "1 osoba")
        self.assertEqual(post.get_cena_display(), "\u015arednio")

    def test_form_exposes_new_choice_fields(self):
        # Sprawdzamy, czy formularz udostępnia wszystkie ważne pola wyboru.
        form = CreatePost()
        filmowe_tagi = dict(Post.TAG_CHOICES[0][1])

        self.assertIn("tagi", form.fields)
        self.assertIn("podtag_anime", form.fields)
        self.assertIn("okazja", form.fields)
        self.assertIn("liczba_osob", form.fields)
        self.assertIn("cena", form.fields)
        self.assertEqual(filmowe_tagi["anime"], "Anime")
        self.assertEqual(filmowe_tagi["animacja"], "Animacja")
        self.assertFalse(form.fields["cena"].required)

    def test_form_clears_anime_subtag_for_non_anime_tag(self):
        # Ten test pilnuje, żeby podtag anime nie został przy zwykłym tagu akcji.
        form = CreatePost(
            data={
                "category": "film",
                "title": "Spider-Man",
                "tagi": "akcja",
                "podtag_anime": "shonen",
                "okazja": "solo",
                "liczba_osob": "1_osoba",
                "cena": "tanio",
                "body": "Film akcji o superbohaterze.",
            }
        )

        self.assertTrue(form.is_valid())
        post = form.save()
        self.assertEqual(post.podtag_anime, "")


# Drugi zestaw testów sprawdza ograniczenia i zachowanie widoku edycji wpisu.
class PostEditViewTests(TestCase):
    def setUp(self):
        # Przygotowujemy autora, innego użytkownika i przykładowy wpis do edycji.
        self.author = User.objects.create_user(username="martina", password="tajnehaslo123")
        self.other_user = User.objects.create_user(username="anna", password="innehaslo123")
        self.post = Post.objects.create(
            category="serial",
            title="Death Note",
            body="Klasyczne anime psychologiczne.",
            tagi="anime",
            podtag_anime="seinen",
            okazja="solo",
            liczba_osob="1_osoba",
            cena="za_darmo",
            author=self.author,
        )

    def test_author_can_edit_own_post(self):
        # Autor wpisu powinien móc zapisać zmiany we własnej pozycji katalogu.
        self.client.login(username="martina", password="tajnehaslo123")

        response = self.client.post(
            reverse("posts:edit-post", kwargs={"slug": self.post.slug}),
            data={
                "category": "serial",
                "title": "Death Note Extended",
                "tagi": "anime",
                "podtag_anime": "fantasy",
                "okazja": "solo",
                "liczba_osob": "1_osoba",
                "cena": "za_darmo",
                "body": "Nowy opis wpisu po edycji.",
            },
        )

        self.assertRedirects(response, reverse("posts:page", kwargs={"slug": self.post.slug}))
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Death Note Extended")
        self.assertEqual(self.post.podtag_anime, "fantasy")
        self.assertEqual(self.post.author, self.author)

    def test_non_author_cannot_open_edit_page(self):
        # Obcy użytkownik nie powinien dostać dostępu do edycji cudzego wpisu.
        self.client.login(username="anna", password="innehaslo123")

        response = self.client.get(reverse("posts:edit-post", kwargs={"slug": self.post.slug}))

        self.assertEqual(response.status_code, 404)

    def test_detail_page_shows_edit_button_only_for_author(self):
        # Na stronie szczegółów przycisk edycji ma widzieć tylko autor wpisu.
        self.client.login(username="martina", password="tajnehaslo123")

        response = self.client.get(reverse("posts:page", kwargs={"slug": self.post.slug}))

        self.assertContains(response, reverse("posts:edit-post", kwargs={"slug": self.post.slug}))

    def test_author_can_delete_own_post(self):
        self.client.login(username="martina", password="tajnehaslo123")

        response = self.client.post(
            reverse("posts:delete-post", kwargs={"slug": self.post.slug})
        )

        self.assertRedirects(response, reverse("posts:list"))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_non_author_cannot_delete_post(self):
        self.client.login(username="anna", password="innehaslo123")

        response = self.client.post(
            reverse("posts:delete-post", kwargs={"slug": self.post.slug})
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())
