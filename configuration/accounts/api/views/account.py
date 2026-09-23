"""Account API views."""

from rest_framework import permissions
from rest_framework.generics import RetrieveUpdateAPIView

from accounts.api.serializers import AccountSerializer


class AccountAPIView(RetrieveUpdateAPIView):
    """Retrieve and update the authenticated user's account."""

    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return the currently authenticated user."""
        return self.request.user