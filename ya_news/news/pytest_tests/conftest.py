import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.test import Client
from django.contrib.auth import get_user_model

from news.models import News, Comment


User = get_user_model()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username="Автор")


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def news_page():
    news_page = News.objects.create(
        title="Заголовок новости",
        text="Текст новости",
    )
    return news_page


@pytest.fixture
def comment(author, news_page):
    comment = Comment.objects.create(
        news=news_page,
        author=author,
        text="Текст",
    )
    return comment


@pytest.fixture
def news():
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f"Новость {index}",
            text=f"Текст новости {index}",
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def form_data(news_page, author):
    return {
        "news": news_page,
        "author": author,
        "text": "Текст",
    }


@pytest.fixture
def pk_for_args(comment):
    return (comment.pk,)
