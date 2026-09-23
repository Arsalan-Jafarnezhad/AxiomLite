"""Public profile URLs."""

from django.urls import path

from accounts.views.profile import ProfileView

urlpatterns = [
    path(
        "profiles/<str:username>/",
        ProfileView.as_view(),
        name="profile",
    ),
]