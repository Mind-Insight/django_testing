from http import HTTPStatus

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING
from .mixins import create_users

User = get_user_model()


class TestLogic(TestCase):
    @classmethod
    @create_users
    def setUpTestData(cls, author, author_client, user, user_client):
        cls.author_client = author_client
        cls.user_client = user_client
        cls.form_data = {
            "text": "Текст",
            "title": "Название",
            "slug": "note-slug",
            "author": author,
        }

    def test_authenticated_user_can_create_note(self):
        url = reverse("notes:add")
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse("notes:success"))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data["title"])
        self.assertEqual(new_note.text, self.form_data["text"])
        self.assertEqual(new_note.slug, self.form_data["slug"])
        self.assertEqual(new_note.author, self.form_data["author"])

    def test_anonymous_user_cannot_create_note(self):
        url = reverse("notes:add")
        response = self.client.post(url, self.form_data)
        login_url = reverse("users:login")
        expected_url = f"{login_url}?next={url}"
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        note = Note.objects.create(**self.form_data)
        url = reverse("notes:add")
        self.form_data["slug"] = note.slug
        response = self.author_client.post(url, data=self.form_data)
        self.assertFormError(
            response, "form", "slug", errors=(note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        url = reverse("notes:add")
        self.form_data.pop("slug")
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse("notes:success"))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data["title"])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        note = Note.objects.create(**self.form_data)
        url = reverse("notes:edit", args=(note.slug,))
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse("notes:success"))
        note.refresh_from_db()
        self.assertEqual(note.title, self.form_data["title"])
        self.assertEqual(note.text, self.form_data["text"])
        self.assertEqual(note.slug, self.form_data["slug"])

    def test_author_can_delete_note(self):
        note = Note.objects.create(**self.form_data)
        url = reverse("notes:delete", args=(note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse("notes:success"))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_edit_note(self):
        note = Note.objects.create(**self.form_data)
        url = reverse("notes:edit", args=(note.slug,))
        response = self.user_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=note.id)
        self.assertEqual(note.title, note_from_db.title)
        self.assertEqual(note.text, note_from_db.text)
        self.assertEqual(note.slug, note_from_db.slug)

    def test_other_user_cant_delete_note(self):
        note = Note.objects.create(**self.form_data)
        url = reverse("notes:delete", args=(note.slug,))
        response = self.user_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
