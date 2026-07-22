import pytest

from tests.helpers import make_summary

pytestmark = pytest.mark.django_db

LIST = "/api/summaries"
TAGS = "/api/tags"


def test_filter_by_tag(api, make_user):
    user = make_user()
    make_summary(user, title="Prod book", tags=["productivity"], published=True)
    make_summary(user, title="Hist book", tags=["history"], published=True)

    resp = api.get(f"{LIST}?tag=productivity")
    titles = [s["title"] for s in resp.json()["results"]]
    assert titles == ["Prod book"]


def test_tag_list_with_counts(api, make_user):
    user = make_user()
    make_summary(user, title="A", tags=["productivity"], published=True)
    make_summary(user, title="B", tags=["productivity"], published=True)
    make_summary(user, title="C", tags=["history"], published=False)  # unpublished

    resp = api.get(TAGS)
    assert resp.status_code == 200
    counts = {t["name"]: t["summary_count"] for t in resp.json()}
    assert counts["productivity"] == 2
    # tag exists but its only summary is unpublished -> count 0
    assert counts["history"] == 0


def test_tag_has_slug(api, make_user):
    user = make_user()
    make_summary(user, title="A", tags=["Deep Focus"], published=True)
    resp = api.get(TAGS)
    slugs = {t["slug"] for t in resp.json()}
    assert "deep-focus" in slugs
