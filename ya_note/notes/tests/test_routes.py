from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from .mixins import create_users


User = get_user_model()


HOME_URL = reverse("notes:home")
LOGIN_URL = reverse("users:login")
LOGOUT_URL = reverse("users:logout")
SIGNUP_URL = reverse("users:signup")
LIST_URL = reverse("notes:list")
ADD_URL = reverse("notes:add")
SUCCESS_URL = reverse("notes:success")
DETAIL_URL = reverse("notes:detail", args=("note_slug",))
EDIT_URL = reverse("notes:edit", args=("note_slug",))
DELETE_URL = reverse("notes:delete", args=("note_slug",))


class TestRoutes(TestCase):
    @classmethod
    @create_users
    def setUpTestData(cls, author, author_client, user, user_client):
        cls.author = author
        cls.author_client = author_client
        cls.user_client = user_client
        cls.note = Note.objects.create(
            title="Название",
            text="Текст",
            author=cls.author,
            slug="note_slug",
        )

    def test_pages_avaliability_for_different_users(self):
        clients = [
            (self.client, (HOME_URL, LOGIN_URL, LOGOUT_URL, SIGNUP_URL)),
            (self.user_client, (LIST_URL, ADD_URL, SUCCESS_URL)),
            (self.author_client, (DETAIL_URL, EDIT_URL, DELETE_URL)),
        ]

        for client, urls in clients:
            for url in urls:
                with self.subTest(url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirects_for_anonymous_user(self):
        for url in (
            LIST_URL,
            SUCCESS_URL,
            ADD_URL,
            DETAIL_URL,
            EDIT_URL,
            DELETE_URL,
        ):
            with self.subTest(url=url):
                expected_url = f"{LOGIN_URL}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
