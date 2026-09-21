from django.utils import timezone

from accounts.models.soft_delete import SoftDeleteQuerySet


class UserQuerySet(SoftDeleteQuerySet):
    """QuerySet providing reusable user filters and bulk operations."""

    def active(self) -> UserQuerySet:
        """Return users that are active."""
        return self.filter(is_active=True)

    def inactive(self) -> UserQuerySet:
        """Return users that are inactive."""
        return self.filter(is_active=False)

    def staff(self) -> UserQuerySet:
        """Return users with Django admin access."""
        return self.filter(is_staff=True)

    def non_staff(self) -> UserQuerySet:
        """Return users without Django admin access."""
        return self.filter(is_staff=False)

    def superusers(self) -> UserQuerySet:
        """Return users with superuser privileges."""
        return self.filter(is_superuser=True)

    def verified(self) -> UserQuerySet:
        """Return users whose email/account is verified."""
        return self.filter(is_verified=True)

    def unverified(self) -> UserQuerySet:
        """Return users whose account is not verified."""
        return self.filter(is_verified=False)

    def email_verified(self) -> UserQuerySet:
        """Return users with a verified email address."""
        return self.filter(email_verified_at__isnull=False)

    def email_unverified(self) -> UserQuerySet:
        """Return users without a verified email address."""
        return self.filter(email_verified_at__isnull=True)

    def phone_verified(self) -> UserQuerySet:
        """Return users with a verified phone number."""
        return self.filter(phone_number_verified_at__isnull=False)

    def phone_unverified(self) -> UserQuerySet:
        """Return users without a verified phone number."""
        return self.filter(phone_number_verified_at__isnull=True)

    def with_phone(self) -> UserQuerySet:
        """Return users who have a phone number."""
        return self.filter(phone_number__isnull=False).exclude(phone_number="")

    def without_phone(self) -> UserQuerySet:
        """Return users who do not have a phone number."""
        return self.filter(phone_number__isnull=True)

    def sms_subscribers(self) -> UserQuerySet:
        """Return active users who accept SMS notifications."""
        return self.active().filter(
            accepts_sms=True,
        )

    def marketing_subscribers(self) -> UserQuerySet:
        """Return active users who accept marketing emails."""
        return self.active().filter(
            accepts_marketing_emails=True,
        )

    def active_verified(self) -> UserQuerySet:
        """Return active and verified users."""
        return self.active().verified()

    def active_staff(self) -> UserQuerySet:
        """Return active staff users."""
        return self.active().staff()

    def active_superusers(self) -> UserQuerySet:
        """Return active superusers."""
        return self.active().superusers()

    def recently_active(
        self,
        *,
        since,
    ) -> UserQuerySet:
        """Return users active since the given datetime."""
        return self.filter(
            last_activity_at__gte=since,
        )

    def never_active(self) -> UserQuerySet:
        """Return users who have never recorded activity."""
        return self.filter(
            last_activity_at__isnull=True,
        )

    def search(
        self,
        query: str,
    ) -> UserQuerySet:
        """
        Search users by email, username, first name, or last name.

        The caller should provide a non-empty search string.
        """
        from django.db.models import Q

        query = query.strip()

        if not query:
            return self.none()

        return self.filter(
            Q(email__icontains=query)
            | Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

    def for_authentication(self) -> UserQuerySet:
        """
        Return users eligible for normal authentication.

        A user must be active and not soft-deleted.
        """
        return self.active()

    def mark_inactive(self) -> int:
        """Deactivate all users in this queryset."""
        return self.update(is_active=False)

    def mark_active(self) -> int:
        """Activate all users in this queryset."""
        return self.update(is_active=True)

    def mark_verified(self) -> int:
        """Verify all users in this queryset."""
        return self.update(
            is_verified=True,
            email_verified_at=timezone.now(),
        )

    def by_username(self, username):
        return self.filter(username__iexact=username)

    def get_by_username(self, username):
        """Case-insensitive lookup returning ``None`` instead of raising."""
        return self.by_username(username).first()
