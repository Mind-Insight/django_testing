from django.test import Client
from django.contrib.auth.models import User


def create_users(func):
    def wrapper(cls):
        author = User.objects.create(username="Автор")
        author_client = Client()
        author_client.force_login(author)
        user = User.objects.create(username="Пользователь")
        user_client = Client()
        user_client.force_login(user)

        func(cls, author, author_client, user, user_client)

    return wrapper
