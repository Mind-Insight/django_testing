import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name", ("news:home", "users:login", "users:logout", "users:signup")
)
def test_pages_avaliability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_page_avaliability_for_anonymous_user(client, news_page):
    url = reverse("news:detail", args=(news_page.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("name", ("news:delete", "news:edit"))
def test_edit_delete_comment_redirect_for_anonymous(client, comment, name):
    login_url = reverse("users:login")
    url = reverse(name, args=(comment.pk,))
    expected_url = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    "parametrized_client, expected_status",
    (
        (pytest.lazy_fixture("admin_client"), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture("author_client"), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize("name", ("news:delete", "news:edit"))
def test_edit_delete_pages_avaliability_for_different_users(
    parametrized_client, expected_status, name, comment
):
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status
