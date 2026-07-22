import pytest

from summaries.models import Tag
from tests.helpers import make_summary

pytestmark = pytest.mark.django_db


def test_str_methods(make_user):
    user = make_user(username="stringy")
    user.save()  # re-save exercises the profile signal's "not created" branch
    tag = Tag.objects.create(name="Sci-Fi")
    assert str(tag) == "Sci-Fi"
    summary = make_summary(user, title="My Book", published=True)
    assert str(summary) == "My Book"
    assert "stringy" in str(user.profile)


def test_register_duplicate_email(api, make_user):
    make_user(username="e1", email="dup@example.com")
    resp = api.post(
        "/api/auth/register",
        {"username": "e2", "email": "dup@example.com", "password": "sup3rsecret"},
        format="json",
    )
    assert resp.status_code == 400


def test_create_summary_skips_blank_tags(auth_client):
    client, _ = auth_client
    resp = client.post(
        "/api/summaries",
        {"title": "T", "author": "A", "body": "B", "tags": ["   ", "real"]},
        format="json",
    )
    assert resp.status_code == 201
    assert {t["name"] for t in resp.json()["tags"]} == {"real"}


def test_partial_update_without_tags_keeps_them(auth_client):
    client, user = auth_client
    summary = make_summary(user, title="Old", tags=["keep"], published=False)
    resp = client.patch(
        f"/api/summaries/{summary.id}", {"title": "New title"}, format="json"
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "New title"
    # Tags untouched because none were supplied.
    assert {t["name"] for t in resp.json()["tags"]} == {"keep"}


def test_publish_others_published_summary_403(other_client, make_user):
    client, _ = other_client
    owner = make_user(username="owner2")
    summary = make_summary(owner, title="Theirs", published=True)
    resp = client.post(f"/api/summaries/{summary.id}/publish")
    assert resp.status_code == 403
