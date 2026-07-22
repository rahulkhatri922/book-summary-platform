from django.urls import path

from .views import MyProfileView, PublicProfileView

urlpatterns = [
    path("profile/me", MyProfileView.as_view(), name="my-profile"),
    path("users/<int:user_id>/profile", PublicProfileView.as_view(), name="user-profile"),
]
