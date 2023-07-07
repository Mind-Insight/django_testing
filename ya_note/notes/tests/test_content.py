from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm
from .mixins import create_users

User = get_user_model()


LIST_URL = reverse("notes:list")
ADD_URL = reverse("notes:add")
EDIT_URL = reverse("notes:edit", args=("note_slug",))


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
        response = self.author_client.get(LIST_URL)
        self.assertIn(self.note, response.context["object_list"])

    def test_note_not_in_list_for_another_user(self):
        response = self.user_client.get(LIST_URL)
        self.assertNotIn(self.note, response.context["object_list"])

    def test_note_pages_contain_form(self):
        for url in (ADD_URL, EDIT_URL):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn("form", response.context)
                self.assertIsInstance(response.context["form"], NoteForm)
