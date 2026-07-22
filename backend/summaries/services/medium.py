"""Medium cross-posting service.

Posts a published summary to the Medium API using the author's per-user
integration token (stored on their profile). Behaviour:

* If the profile has a token, POST to the real Medium API. Failures are caught
  and logged; the caller still keeps the summary published locally.
* If there is no token and ``MEDIUM_MOCK`` is on (the default), return a
  plausible fake URL so the feature is demoable end-to-end without a real token
  (Medium's public posting API is effectively discontinued).
* If there is no token and mock mode is off, skip and return None.

The function never raises — it returns the Medium URL on success or None.
"""
import logging

import requests
from django.conf import settings
from django.utils.text import slugify

logger = logging.getLogger(__name__)

TIMEOUT = 15


def _get_author_id(token):
    """Resolve the Medium user id for the token via GET /me."""
    resp = requests.get(
        f"{settings.MEDIUM_API_BASE}/me",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["data"]["id"]


def _mock_url(summary):
    return (
        f"https://medium.com/@{summary.created_by.username}/"
        f"{slugify(summary.title)}-{summary.pk}"
    )


def cross_post_to_medium(summary, profile):
    """Cross-post ``summary`` to Medium. Returns the post URL or None."""
    token = getattr(profile, "medium_token", "") if profile else ""

    if not token:
        if settings.MEDIUM_MOCK:
            url = _mock_url(summary)
            logger.info(
                "MEDIUM_MOCK enabled and no token set; returning mock URL %s", url
            )
            return url
        logger.info(
            "No Medium token for user %s; skipping cross-post.", summary.created_by_id
        )
        return None

    try:
        author_id = profile.medium_user_id or _get_author_id(token)
        resp = requests.post(
            f"{settings.MEDIUM_API_BASE}/users/{author_id}/posts",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={
                "title": summary.title,
                "contentFormat": "markdown",
                "content": summary.body,
                "tags": [t.name for t in summary.tags.all()][:5],
                "publishStatus": "public",
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        url = resp.json().get("data", {}).get("url")
        logger.info("Cross-posted summary %s to Medium: %s", summary.pk, url)
        return url
    except Exception as exc:  # noqa: BLE001 - never let a Medium failure break publish
        logger.error("Medium cross-post failed for summary %s: %s", summary.pk, exc)
        return None
