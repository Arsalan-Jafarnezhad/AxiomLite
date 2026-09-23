"""Profile API views."""

from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView

from accounts.api.serializers import (
    ProfileSerializer,
    PublicProfileSerializer,
)
from accounts.models import Profile


class ProfileAPIView(RetrieveUpdateAPIView):
    """Retrieve and update the authenticated user's profile."""

    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return the authenticated user's profile."""
        return get_object_or_404(
            Profile.objects.select_related("user"),
            user=self.request.user,
        )


class PublicProfileAPIView(RetrieveAPIView):
    """Retrieve a user's public profile."""

    serializer_class = PublicProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        """Return the requested user's profile."""
        username = self.kwargs["username"]

        return get_object_or_404(
            Profile.objects.select_related("user"),
            user__username__iexact=username,
            user__is_active=True,
        )