from unittest import mock

import pytest
import requests

from tests.helpers import make_summary

pytestmark = pytest.mark.django_db

LIST = "/api/summaries"


def _publish_url(summary_id):
    return f"{LIST}/{summary_id}/publish"


def _mock_response(json_data):
    resp = mock.Mock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = json_data
    return resp


def test_publish_sets_published_and_mock_url(auth_client, settings):
    settings.MEDIUM_MOCK = True
    client, user = auth_client
    s = make_summary(user, title="Draft", published=False)

    resp = client.post(_publish_url(s.id))
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_published"] is True
    # No token + mock mode -> a fake medium.com URL.
    assert "medium.com" in data["medium_url"]
    s.refresh_from_db()
    assert s.is_published is True


@mock.patch("summaries.services.medium.requests.post")
def test_publish_calls_real_medium_with_token(mock_post, auth_client):
    client, user = auth_client
    profile = user.profile
    profile.medium_token = "tok-123"
    profile.medium_user_id = "author-1"  # set so /me is skipped
    profile.save()
    mock_post.return_value = _mock_response(
        {"data": {"url": "https://medium.com/@alice/real-post-abc"}}
    )

    s = make_summary(user, title="Draft", published=False)
    resp = client.post(_publish_url(s.id))

    assert resp.status_code == 200
    assert resp.json()["medium_url"] == "https://medium.com/@alice/real-post-abc"
    assert mock_post.called
    # Body should have been sent as markdown.
    _, kwargs = mock_post.call_args
    assert kwargs["json"]["contentFormat"] == "markdown"


@mock.patch("summaries.services.medium.requests.get")
@mock.patch("summaries.services.medium.requests.post")
def test_publish_resolves_author_id_via_me(mock_post, mock_get, auth_client):
    client, user = auth_client
    profile = user.profile
    profile.medium_token = "tok-123"  # no medium_user_id -> must call /me
    profile.save()
    mock_get.return_value = _mock_response({"data": {"id": "resolved-id"}})
    mock_post.return_value = _mock_response(
        {"data": {"url": "https://medium.com/@alice/xyz"}}
    )

    s = make_summary(user, title="Draft", published=False)
    resp = client.post(_publish_url(s.id))

    assert resp.status_code == 200
    assert resp.json()["medium_url"] == "https://medium.com/@alice/xyz"
    assert mock_get.called  # /me was hit to resolve the author id
    # The resolved id must appear in the posts URL.
    assert "resolved-id" in mock_post.call_args[0][0]


@mock.patch("summaries.services.medium.requests.post")
def test_publish_survives_medium_failure(mock_post, auth_client):
    client, user = auth_client
    profile = user.profile
    profile.medium_token = "tok-123"
    profile.medium_user_id = "author-1"
    profile.save()
    mock_post.side_effect = requests.RequestException("boom")

    s = make_summary(user, title="Draft", published=False)
    resp = client.post(_publish_url(s.id))

    # Published locally despite the Medium error; no URL recorded.
    assert resp.status_code == 200
    assert resp.json()["is_published"] is True
    assert resp.json()["medium_url"] is None
    s.refresh_from_db()
    assert s.is_published is True


def test_publish_skips_without_token_when_mock_off(auth_client, settings):
    settings.MEDIUM_MOCK = False
    client, user = auth_client
    s = make_summary(user, title="Draft", published=False)
    resp = client.post(_publish_url(s.id))
    assert resp.status_code == 200
    assert resp.json()["is_published"] is True
    assert resp.json()["medium_url"] is None


def test_cannot_publish_others_summary(other_client, make_user):
    client, _ = other_client
    owner = make_user(username="owner")
    s = make_summary(owner, title="Theirs", published=False)
    resp = client.post(_publish_url(s.id))
    assert resp.status_code in (403, 404)
