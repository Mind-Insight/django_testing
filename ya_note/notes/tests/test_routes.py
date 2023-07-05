from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="Пользователь")
        cls.author = User.objects.create(username="Автор")
        cls.note = Note.objects.create(
            title="Название",
            text="Текст",
            author=cls.author,
            slug="note_slug",
        )

    def test_pages_avaliability_for_anonymous_user(self):
        for name in (
            "notes:home",
            "users:login",
            "users:logout",
            "users:signup",
        ):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_avaliability_for_auth_user(self):
        self.client.force_login(self.user)
        for name in ("notes:list", "notes:add", "notes:success"):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_avaliability_for_author(self):
        self.client.force_login(self.author)
        for name in ("notes:detail", "notes:edit", "notes:delete"):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirects_for_anonymous_user(self):
        login_url = reverse("users:login")
        urls = (
            ("notes:list", None),
            ("notes:success", None),
            ("notes:add", None),
            ("notes:detail", (self.note.slug,)),
            ("notes:edit", (self.note.slug,)),
            ("notes:delete", (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                expected_url = f"{login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
