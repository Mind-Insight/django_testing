from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse

from news.forms import BAD_WORDS
from news.models import Comment
from .constants import LOGIN_URL


@pytest.mark.django_db
def test_anonymous_user_cant_send_comment(client, news_page, form_data):
    assert Comment.objects.count() == 0
    login_url = LOGIN_URL
    url = reverse("news:detail", args=(news_page.pk,))
    response = client.post(url, data=form_data)
    expected_url = f"{login_url}?next={url}"
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_auth_user_can_send_message(news_page, form_data, author_client):
    url = reverse("news:detail", args=(news_page.pk,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f"{url}#comments")
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.news == form_data.get("news")
    assert comment.author == form_data.get("author")
    assert comment.text == form_data.get("text")


def test_comment_cant_contain_bad_words(author_client, news_page):
    bad_words_data = {"text": f"Какой-то текст, {BAD_WORDS[0]}, еще текст"}
    url = reverse("news:detail", args=(news_page.pk,))
    response = author_client.post(url, data=bad_words_data)
    assert "form" in response.context
    assert "text" in response.context["form"].errors
    assert Comment.objects.count() == 0


def test_author_can_delete_his_comments(author_client, comment, news_page):
    assert Comment.objects.count() != 0
    url = reverse("news:delete", args=(comment.pk,))
    news_url = reverse("news:detail", args=(news_page.pk,))
    response = author_client.delete(url)
    assertRedirects(response, news_url + "#comments")
    assert Comment.objects.count() == 0


def test_author_can_edit_his_comments(
    author_client, comment, news_page, form_data
):
    url = reverse("news:edit", args=(comment.pk,))
    news_url = reverse("news:detail", args=(news_page.pk,))
    form_data["text"] = "New Text"
    response = author_client.post(url, data=form_data)
    assertRedirects(response, news_url + "#comments")
    comment.refresh_from_db()
    assert comment.text == form_data["text"]
    assert comment.news == form_data["news"]
    assert comment.author == form_data["author"]


@pytest.mark.django_db
def test_auth_user_cant_edit_other_comments(admin_client, comment, form_data):
    url = reverse("news:edit", args=(comment.pk,))
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db
    assert comment.text == form_data["text"]


@pytest.mark.django_db
def test_auth_user_cant_delete_other_comments(
    admin_client, comment, form_data
):
    url = reverse("news:delete", args=(comment.pk,))
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
