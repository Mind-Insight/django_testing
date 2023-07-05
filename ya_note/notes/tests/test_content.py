from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from notes.models import Note
from .mixins import create_users

User = get_user_model()


class TestContent(TestCase):
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

    def test_note_in_list_for_author(self):
        url = reverse("notes:list")
        response = self.author_client.get(url)
        self.assertIn(self.note, response.context["object_list"])

    def test_note_not_in_list_for_another_user(self):
        url = reverse("notes:list")
        response = self.user_client.get(url)
        self.assertNotIn(self.note, response.context["object_list"])

    def test_note_pages_contain_form(self):
        urls = (
            ("notes:add", None),
            ("notes:edit", (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn("form", response.context)
