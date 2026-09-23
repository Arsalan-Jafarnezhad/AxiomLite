"""Public user profile views."""

from typing import Any

from django.contrib.auth import get_user_model
from django.http import Http404

from django.views.generic import DetailView

User = get_user_model()


class ProfileView(DetailView):
    """Display a user's public profile."""

    model = User
    context_object_name = "profile_user"

    def get_object(self, queryset=None):
        """Retrieve a user by case-insensitive username."""
        username = self.kwargs["username"]

        user = (
            User.objects
            .by_username(username)
            .first()
        )

        if user is None:
            raise Http404("User not found.")

        return user

    def get_template_names(self) -> list[str]:
        """Select the public or private profile template."""
        if self.object.profile.is_private:
            return ["accounts/profile/secure.html"]

        return ["accounts/profile/public.html"]

    def get_context_data(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Add ownership information to the context."""
        context = super().get_context_data(**kwargs)

        context["is_own_profile"] = (
            self.request.user == self.object
        )

        return context