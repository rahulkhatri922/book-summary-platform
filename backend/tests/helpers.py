"""Shared test helpers."""
from summaries.models import Summary, Tag
from summaries.search import update_search_vector


def make_summary(user, title="A Title", author="An Author", body="Some body text",
                 published=True, tags=None):
    summary = Summary.objects.create(
        title=title,
        author=author,
        body=body,
        created_by=user,
        is_published=published,
    )
    if tags:
        summary.tags.set([Tag.objects.get_or_create(name=t)[0] for t in tags])
    update_search_vector(summary)
    return summary
