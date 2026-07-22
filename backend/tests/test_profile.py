import pytest

from tests.helpers import make_summary

pytestmark = pytest.mark.django_db


def test_public_profile_lists_published_summaries(api, make_user):
    user = make_user(username="author1")
    make_summary(user, title="Public book", published=True)
    make_summary(user, title="Private draft", published=False)

    resp = api.get(f"/api/users/{user.id}/profile")
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "author1"
    titles = [s["title"] for s in data["summaries"]]
    assert "Public book" in titles
    assert "Private draft" not in titles


def test_public_profile_404_for_unknown_user(api):
    assert api.get("/api/users/99999/profile").status_code == 404


def test_my_profile_requires_auth(api):
    assert api.get("/api/profile/me").status_code == 401


def test_update_my_profile_sets_medium_token(auth_client):
    client, user = auth_client
    resp = client.patch(
        "/api/profile/me",
        {"bio": "I read books.", "medium_token": "tok-xyz"},
        format="json",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["bio"] == "I read books."
    assert data["has_medium_token"] is True
    # Token itself is write-only, never echoed back.
    assert "medium_token" not in data
    user.profile.refresh_from_db()
    assert user.profile.medium_token == "tok-xyz"
