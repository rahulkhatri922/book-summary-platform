import pytest

from tests.helpers import make_summary

pytestmark = pytest.mark.django_db

LIST = "/api/summaries"


def test_full_text_search_matches_title_and_body(api, make_user):
    user = make_user()
    make_summary(
        user,
        title="Atomic Habits",
        body="Tiny changes compound into remarkable results over time.",
        published=True,
    )
    make_summary(
        user,
        title="Sapiens",
        body="A history of humankind and shared fictions like money.",
        published=True,
    )

    resp = api.get(f"{LIST}?search=compound habits")
    assert resp.status_code == 200
    titles = [s["title"] for s in resp.json()["results"]]
    assert "Atomic Habits" in titles
    assert "Sapiens" not in titles


def test_search_matches_body_terms(api, make_user):
    user = make_user()
    make_summary(user, title="Sapiens", body="shared fictions like money and empire",
                 published=True)
    make_summary(user, title="Deep Work", body="focus without distraction",
                 published=True)
    resp = api.get(f"{LIST}?search=empire")
    titles = [s["title"] for s in resp.json()["results"]]
    assert titles == ["Sapiens"]


def test_search_no_results(api, make_user):
    user = make_user()
    make_summary(user, title="Atomic Habits", body="compounding gains", published=True)
    resp = api.get(f"{LIST}?search=quantummechanics")
    assert resp.json()["results"] == []


def test_search_excludes_unpublished(api, make_user):
    user = make_user()
    make_summary(user, title="Hidden gem", body="unique keyword zephyr",
                 published=False)
    resp = api.get(f"{LIST}?search=zephyr")
    assert resp.json()["results"] == []
