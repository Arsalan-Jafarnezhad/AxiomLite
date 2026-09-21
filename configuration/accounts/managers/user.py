from __future__ import annotations

from typing import Any

from django.contrib.auth.base_user import BaseUserManager
from accounts.querysets.user import UserQuerySet

class UserManager(BaseUserManager.from_queryset(UserQuerySet)):
    """
    Manager for the custom email-first User model.

    The default manager exposes only non-deleted users because the
    underlying UserQuerySet inherits SoftDeleteQuerySet.
    """

    use_in_migrations = True

    def _normalize_email(self, email: str) -> str:
        """
        Normalize an email address for application-level uniqueness.

        This project treats email addresses as case-insensitive.
        """
        if not isinstance(email, str):
            raise TypeError("Email must be a string.")

        email = email.strip()

        if not email:
            raise ValueError("Email address is required.")

        return email.lower()

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ):
        """
        Create and save a normal user.

        The user's password is always passed through Django's password
        hashing mechanism.
        """
        email = self._normalize_email(email)

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", False)

        if extra_fields.get("is_staff"):
            raise ValueError(
                "create_user() cannot create a staff user."
            )

        if extra_fields.get("is_superuser"):
            raise ValueError(
                "create_user() cannot create a superuser."
            )

        user = self.model(
            email=email,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ):
        """
        Create and save a Django superuser.
        """
        email = self._normalize_email(email)

        if not password:
            raise ValueError(
                "Superuser password must be provided."
            )

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True."
            )

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True."
            )

        if extra_fields.get("is_active") is not True:
            raise ValueError(
                "Superuser must have is_active=True."
            )

        user = self.model(
            email=email,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def get_by_email(self, email: str):
        """Return a non-deleted user by normalized email."""
        email = self._normalize_email(email)

        return self.get(email=email)

    def email_exists(
        self,
        email: str,
        *,
        include_deleted: bool = False,
    ) -> bool:
        """
        Check whether an email address exists.

        By default, soft-deleted users are excluded.
        """
        email = self._normalize_email(email)

        manager = self

        if include_deleted:
            manager = self.model.all_objects

        return manager.filter(email=email).exists()

    def username_exists(
        self,
        username: str,
        *,
        include_deleted: bool = False,
    ) -> bool:
        """Check whether a username exists."""
        username = username.strip()

        if not username:
            return False

        manager = self

        if include_deleted:
            manager = self.model.all_objects

        return manager.filter(
            username__iexact=username,
        ).exists()

    def active_by_email(self, email: str):
        """Return an active, non-deleted user by email."""
        email = self._normalize_email(email)

        return self.active().get(email=email)

    def verified_by_email(self, email: str):
        """Return a verified, non-deleted user by email."""
        email = self._normalize_email(email)

        return self.verified().get(email=email)

    def get_or_create_by_email(
        self,
        email: str,
        defaults: dict[str, Any] | None = None,
        **extra_fields: Any,
    ):
        """
        Get or create a user using a normalized email address.
        """
        email = self._normalize_email(email)

        fields = {
            **(defaults or {}),
            **extra_fields,
        }

        return self.get_or_create(
            email=email,
            defaults=fields,
        )

    def create_if_not_exists(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ):
        """
        Create a user if the email does not already exist.

        Returns:
            tuple[user, created]
        """
        email = self._normalize_email(email)

        user, created = self.get_or_create(
            email=email,
            defaults=extra_fields,
        )

        if created and password is not None:
            user.set_password(password)
            user.save(
                update_fields=["password"],
                using=self._db,
            )

        return user, created