"""URL configuration for the accounts API."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from accounts.api.views import (
    AccountAPIView,
    AddressViewSet,
    ProfileAPIView,
    PublicProfileAPIView,
)

app_name = "api"

router = DefaultRouter()
router.register(
    r"addresses",
    AddressViewSet,
    basename="address",
)

urlpatterns = [
    path("me/", AccountAPIView.as_view(), name="me"),
    path("profile/", ProfileAPIView.as_view(), name="profile"),
    path(
        "profiles/<str:username>/",
        PublicProfileAPIView.as_view(),
        name="public-profile",
    ),
]

urlpatterns += router.urls
