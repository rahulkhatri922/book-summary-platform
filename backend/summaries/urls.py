from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import SummaryViewSet, TagListView

router = SimpleRouter(trailing_slash=False)
router.register("summaries", SummaryViewSet, basename="summary")

urlpatterns = [
    path("tags", TagListView.as_view(), name="tag-list"),
] + router.urls
