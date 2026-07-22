"""PostgreSQL full-text search helpers.

`title` is weighted higher (A) than `body` (B). The search endpoint ranks
results with SearchRank against the stored SearchVectorField (GIN-indexed).
"""
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

SEARCH_CONFIG = "english"


def build_vector():
    return SearchVector("title", weight="A", config=SEARCH_CONFIG) + SearchVector(
        "body", weight="B", config=SEARCH_CONFIG
    )


def update_search_vector(summary):
    """Recompute and store the search vector for a single summary."""
    from .models import Summary

    Summary.objects.filter(pk=summary.pk).update(search_vector=build_vector())


def search_summaries(queryset, query_text):
    """Filter/rank a Summary queryset by a full-text query."""
    query = SearchQuery(query_text, config=SEARCH_CONFIG, search_type="websearch")
    return (
        queryset.annotate(rank=SearchRank("search_vector", query))
        .filter(search_vector=query)
        .order_by("-rank", "-created_at")
    )
