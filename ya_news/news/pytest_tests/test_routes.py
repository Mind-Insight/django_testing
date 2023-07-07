import pytest
from http import HTTPStatus
from django.test import Client

from django.urls import reverse
from pytest_django.asserts import assertRedirects
from .constants import NEWS_HOME, LOGIN_URL, LOGOUT_URL, SIGNUP_URL


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, client, expected_status",
    (
        (NEWS_HOME, Client(), HTTPStatus.OK),
        (LOGIN_URL, Client(), HTTPStatus.OK),
        (LOGOUT_URL, Client(), HTTPStatus.OK),
        (SIGNUP_URL, Client(), HTTPStatus.OK),
        (
            "news:delete",
            pytest.lazy_fixture("admin_client"),
            HTTPStatus.NOT_FOUND,
        ),
        (
            "news:delete",
            pytest.lazy_fixture("author_client"),
            HTTPStatus.OK,
        ),
        (
            "news:edit",
            pytest.lazy_fixture("admin_client"),
            HTTPStatus.NOT_FOUND,
        ),
        (
            "news:edit",
            pytest.lazy_fixture("author_client"),
            HTTPStatus.OK,
        ),
    ),
)
def test_pages_availability_for_different_users(
    url, client, expected_status, pk_for_args
):
    if url in ("news:edit", "news:delete"):
        url = reverse(url, args=pk_for_args)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize("name", ("news:delete", "news:edit"))
def test_edit_delete_comment_redirect_for_anonymous(client, comment, name):
    login_url = reverse("users:login")
    url = reverse(name, args=(comment.pk,))
    expected_url = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_url)
