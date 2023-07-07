import pytest
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from news.models import Comment
from news.forms import CommentForm
from .constants import NEWS_HOME


@pytest.mark.django_db
def test_news_per_page_on_home_page(client, news):
    url = NEWS_HOME
    response = client.get(url)
    object_list = response.context["object_list"]
    news_per_page = len(object_list)
    assert news_per_page == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_sort_from_new_to_old(client, news):
    url = NEWS_HOME
    response = client.get(url)
    object_list = response.context.get("object_list")
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_sort_from_old_to_new(news_page, author, client):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news_page,
            author=author,
            text=f"Текст комментария {index}",
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    url = reverse("news:detail", args=(news_page.pk,))
    response = client.get(url)
    assert "news" in response.context
    news = response.context.get("news")
    all_comments = news.comment_set.all()
    for index in range(len(all_comments) - 1):
        assert all_comments[index].created < all_comments[index + 1].created


@pytest.mark.django_db
def test_anonymous_user_hasnt_comment_form(client, news_page):
    url = reverse("news:detail", args=(news_page.pk,))
    response = client.get(url)
    assert "form" not in response.context


@pytest.mark.django_db
def test_auth_user_has_comment_form(admin_client, news_page):
    url = reverse("news:detail", args=(news_page.pk,))
    response = admin_client.get(url)
    assert "form" in response.context
    assert isinstance(response.context["form"], CommentForm)
