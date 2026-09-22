"""QuerySet definitions for the accounts application."""

from typing import Self

from django.db import models


class UserQuerySet(models.QuerySet):
    """Collection-level operations for the User model."""

    def active(self) -> Self:
        """Return users whose accounts are active."""
        return self.filter(is_active=True)

    def inactive(self) -> Self:
        """Return users whose accounts are inactive."""
        return self.filter(is_active=False)

    def verified(self) -> Self:
        """Return users whose accounts are verified."""
        return self.filter(is_verified=True)

    def unverified(self) -> Self:
        """Return users whose accounts are not verified."""
        return self.filter(is_verified=False)

    def email_verified(self) -> Self:
        """Return users with a verified email address."""
        return self.filter(email_verified_at__isnull=False)

    def email_unverified(self) -> Self:
        """Return users without a verified email address."""
        return self.filter(email_verified_at__isnull=True)

    def phone_verified(self) -> Self:
        """Return users with a verified phone number."""
        return self.filter(phone_number_verified_at__isnull=False)

    def phone_unverified(self) -> Self:
        """Return users without a verified phone number."""
        return self.filter(phone_number_verified_at__isnull=True)

    def staff(self) -> Self:
        """Return staff users."""
        return self.filter(is_staff=True)

    def non_staff(self) -> Self:
        """Return users who are not staff members."""
        return self.filter(is_staff=False)

    def superusers(self) -> Self:
        """Return superusers."""
        return self.filter(is_superuser=True)

    def non_superusers(self) -> Self:
        """Return users who are not superusers."""
        return self.filter(is_superuser=False)

    def official(self) -> Self:
        """Return users belonging to an official account group."""
        return self.filter(
            groups__name__in=[
                "Founder",
                "Owner",
                "Manager",
            ]
        ).distinct()

    def with_profile(self) -> Self:
        """Return users with their related profile loaded."""
        return self.select_related("profile")

    def with_security_data(self) -> Self:
        """Return users with commonly accessed security relations."""
        return self.select_related("profile")

    def by_username(self, username: str) -> Self:
        """Filter users by username case-insensitively."""
        return self.filter(username__iexact=username)

    def by_email(self, email: str) -> Self:
        """Filter users by email case-insensitively."""
        return self.filter(email__iexact=email.strip())

    def email_exists(self, email: str) -> bool:
        """Return whether an active user uses the given email."""
        return self.by_email(email).exists()

    def username_exists(self, username: str) -> bool:
        """Return whether an active user uses the given username."""
        return self.by_username(username).exists()

    def get_by_username(self, username: str):
        """Return the user matching a username or ``None``."""
        return self.by_username(username).first()

    def get_by_email(self, email: str):
        """Return the user matching an email or ``None``."""
        return self.by_email(email).first()

    def searchable(self, query: str) -> Self:
        """
        Return users matching a basic public identity search.

        Searches username, email, first name, and last name.
        """
        from django.db.models import Q

        query = query.strip()

        if not query:
            return self.none()

        return self.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

    def recently_active(self) -> Self:
        """Return users ordered by their most recent activity."""
        return self.exclude(last_activity_at__isnull=True).order_by("-last_activity_at")

    def recently_joined(self) -> Self:
        """Return users ordered by registration date."""
        return self.order_by("-date_joined")

    def by_username(self, username):
        return self.filter(username__iexact=username)

    def get_by_username(self, username):
        """Case-insensitive lookup returning ``None`` instead of raising."""
        return self.by_username(username).first()
