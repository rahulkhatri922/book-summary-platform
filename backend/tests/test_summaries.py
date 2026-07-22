import pytest

from summaries.models import Summary
from tests.helpers import make_summary

pytestmark = pytest.mark.django_db

LIST = "/api/summaries"


def test_create_requires_auth(api):
    resp = api.post(LIST, {"title": "x", "author": "y", "body": "z"}, format="json")
    assert resp.status_code == 401


def test_create_summary(auth_client):
    client, user = auth_client
    resp = client.post(
        LIST,
        {"title": "Deep Work", "author": "Cal Newport", "body": "Focus.",
         "tags": ["productivity", "focus"]},
        format="json",
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Deep Work"
    assert data["body"] == "Focus."
    assert data["created_by"] == user.username
    assert {t["name"] for t in data["tags"]} == {"productivity", "focus"}
    # New summaries start unpublished.
    assert data["is_published"] is False


def test_list_shows_only_published_to_anon(api, make_user):
    user = make_user()
    make_summary(user, title="Published one", published=True)
    make_summary(user, title="Draft one", published=False)
    resp = api.get(LIST)
    assert resp.status_code == 200
    titles = [s["title"] for s in resp.json()["results"]]
    assert "Published one" in titles
    assert "Draft one" not in titles


def test_owner_can_list_own_drafts(auth_client):
    client, user = auth_client
    make_summary(user, title="My draft", published=False)
    resp = client.get(f"{LIST}?mine=true")
    titles = [s["title"] for s in resp.json()["results"]]
    assert "My draft" in titles


def test_retrieve_published(api, make_user):
    user = make_user()
    s = make_summary(user, title="Readable", published=True)
    resp = api.get(f"{LIST}/{s.id}")
    assert resp.status_code == 200
    assert resp.json()["body"] == "Some body text"


def test_retrieve_others_draft_404(other_client, make_user):
    client, _ = other_client
    owner = make_user(username="owner")
    s = make_summary(owner, title="Secret draft", published=False)
    assert client.get(f"{LIST}/{s.id}").status_code == 404


def test_update_own_summary(auth_client):
    client, user = auth_client
    s = make_summary(user, title="Old", published=False)
    resp = client.put(
        f"{LIST}/{s.id}",
        {"title": "New", "author": "A", "body": "Updated body", "tags": ["x"]},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "New"
    s.refresh_from_db()
    assert s.title == "New"


def test_cannot_update_others_summary(other_client, make_user):
    client, _ = other_client
    owner = make_user(username="owner")
    s = make_summary(owner, title="Theirs", published=True)
    resp = client.put(
        f"{LIST}/{s.id}",
        {"title": "Hacked", "author": "A", "body": "b"},
        format="json",
    )
    assert resp.status_code == 403


def test_delete_own_summary(auth_client):
    client, user = auth_client
    s = make_summary(user, published=True)
    assert client.delete(f"{LIST}/{s.id}").status_code == 204
    assert not Summary.objects.filter(id=s.id).exists()


def test_cannot_delete_others_summary(other_client, make_user):
    client, _ = other_client
    owner = make_user(username="owner")
    s = make_summary(owner, published=True)
    assert client.delete(f"{LIST}/{s.id}").status_code == 403


def test_pagination(api, make_user):
    user = make_user()
    for i in range(12):
        make_summary(user, title=f"Book {i}", published=True)
    resp = api.get(f"{LIST}?page=1")
    body = resp.json()
    assert body["count"] == 12
    assert len(body["results"]) == 10  # PAGE_SIZE
    assert body["next"] is not None
