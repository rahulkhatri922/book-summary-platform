from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Summary, Tag
from .permissions import IsOwnerOrReadOnly
from .search import search_summaries, update_search_vector
from .serializers import (
    SummaryDetailSerializer,
    SummaryListSerializer,
    SummaryWriteSerializer,
    TagSerializer,
)
from .services.medium import cross_post_to_medium

TRUTHY = {"1", "true", "yes", "on"}


class SummaryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return SummaryWriteSerializer
        if self.action == "retrieve":
            return SummaryDetailSerializer
        return SummaryListSerializer

    def get_queryset(self):
        qs = Summary.objects.select_related("created_by").prefetch_related("tags")

        if self.action == "list":
            mine = self.request.query_params.get("mine", "").lower() in TRUTHY
            if mine and self.request.user.is_authenticated:
                qs = qs.filter(created_by=self.request.user)
            else:
                qs = qs.filter(is_published=True)

            tag = self.request.query_params.get("tag")
            if tag:
                qs = qs.filter(tags__slug=tag)

            search = self.request.query_params.get("search")
            if search:
                qs = search_summaries(qs, search)
            return qs.distinct()

        # Detail actions: owners can reach their own drafts; others only published.
        if self.request.user.is_authenticated:
            return qs.filter(
                Q(is_published=True) | Q(created_by=self.request.user)
            )
        return qs.filter(is_published=True)

    def create(self, request, *args, **kwargs):
        write = self.get_serializer(data=request.data)
        write.is_valid(raise_exception=True)
        summary = write.save()
        detail = SummaryDetailSerializer(summary, context=self.get_serializer_context())
        return Response(detail.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        write = self.get_serializer(instance, data=request.data, partial=partial)
        write.is_valid(raise_exception=True)
        summary = write.save()
        detail = SummaryDetailSerializer(summary, context=self.get_serializer_context())
        return Response(detail.data)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        # get_object() enforces ownership via IsOwnerOrReadOnly (403 for a
        # published summary owned by someone else, 404 for someone else's draft).
        summary = self.get_object()
        summary.is_published = True
        summary.save(update_fields=["is_published", "updated_at"])
        update_search_vector(summary)

        # Cross-post to Medium; failures are logged inside the service and never
        # prevent local publication.
        profile = getattr(request.user, "profile", None)
        medium_url = cross_post_to_medium(summary, profile)
        if medium_url:
            summary.medium_url = medium_url
            summary.save(update_fields=["medium_url", "updated_at"])

        detail = SummaryDetailSerializer(summary, context=self.get_serializer_context())
        return Response(detail.data)


class TagListView(ListAPIView):
    """GET /api/tags — all tags with a count of published summaries."""

    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Tag.objects.annotate(
            summary_count=Count(
                "summaries", filter=Q(summaries__is_published=True), distinct=True
            )
        ).order_by("name")
