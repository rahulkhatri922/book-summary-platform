import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

pytestmark = pytest.mark.django_db

REGISTER = "/api/auth/register"
LOGIN = "/api/auth/login"
LOGOUT = "/api/auth/logout"


def test_register_success(api):
    resp = api.post(
        REGISTER,
        {"username": "newuser", "email": "new@example.com", "password": "sup3rsecret"},
        format="json",
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["token"]
    assert body["user"]["username"] == "newuser"
    # Profile auto-created by the signal.
    assert User.objects.get(username="newuser").profile is not None


def test_register_duplicate_username(api, make_user):
    make_user(username="dupe")
    resp = api.post(
        REGISTER, {"username": "dupe", "password": "sup3rsecret"}, format="json"
    )
    assert resp.status_code == 400


def test_register_weak_password(api):
    resp = api.post(
        REGISTER, {"username": "weak", "password": "123"}, format="json"
    )
    assert resp.status_code == 400


def test_login_success(api, make_user):
    make_user(username="loginuser")
    resp = api.post(
        LOGIN, {"username": "loginuser", "password": "sup3rsecret"}, format="json"
    )
    assert resp.status_code == 200
    assert resp.json()["token"]


def test_login_wrong_password(api, make_user):
    make_user(username="loginuser")
    resp = api.post(
        LOGIN, {"username": "loginuser", "password": "nope"}, format="json"
    )
    assert resp.status_code == 400


def test_logout_deletes_token(auth_client):
    client, user = auth_client
    assert Token.objects.filter(user=user).exists()
    resp = client.post(LOGOUT)
    assert resp.status_code == 204
    assert not Token.objects.filter(user=user).exists()


def test_logout_requires_auth(api):
    assert api.post(LOGOUT).status_code == 401
