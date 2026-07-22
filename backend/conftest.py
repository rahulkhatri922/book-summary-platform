import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

PASSWORD = "sup3rsecret"


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def make_user(db):
    def _make(username="alice", password=PASSWORD, email=""):
        return User.objects.create_user(
            username=username, password=password, email=email
        )

    return _make


@pytest.fixture
def auth_client(db, make_user):
    """An APIClient authenticated as a fresh user. Returns (client, user)."""
    user = make_user()
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client, user


@pytest.fixture
def other_client(db, make_user):
    user = make_user(username="bob")
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client, user
