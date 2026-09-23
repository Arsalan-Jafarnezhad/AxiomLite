"""Address API views."""

from rest_framework import permissions, viewsets

from accounts.api.serializers import AddressSerializer
from accounts.models import Address


class AddressViewSet(viewsets.ModelViewSet):
    """Manage addresses belonging to the authenticated user."""

    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "public_id"

    def get_queryset(self):
        """Return only addresses belonging to the authenticated user."""
        return Address.objects.filter(
            user=self.request.user,
        ).order_by(
            "-is_default",
            "-created_at",
        )

    def perform_create(self, serializer):
        """Assign the authenticated user to a newly created address."""
        serializer.save(user=self.request.user)