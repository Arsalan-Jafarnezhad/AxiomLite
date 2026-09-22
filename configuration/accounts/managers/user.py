"""Managers for the accounts user model."""

from typing import Any

from django.contrib.auth.base_user import BaseUserManager

from accounts.querysets import UserQuerySet


class UserManager(BaseUserManager.from_queryset(UserQuerySet)):
    """Manager for active, non-deleted users."""

    def get_queryset(self) -> UserQuerySet:
        """Return only non-deleted users."""
        return super().get_queryset().active()

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ):
        """Create and save a regular user."""
        if not email:
            raise ValueError("Email required")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            **extra_fields,
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.is_staff = extra_fields.get("is_staff", False)
        user.is_superuser = extra_fields.get("is_superuser", False)

        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email: str,
        password: str,
        **extra_fields: Any,
    ):
        """Create and save a superuser with required admin flags."""
        if not password:
            raise ValueError("Superuser password required")

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields["is_staff"] is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields["is_superuser"] is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(
            email=email,
            password=password,
            **extra_fields,
        )


class AllUserManager(BaseUserManager.from_queryset(UserQuerySet)):
    """Manager exposing both active and soft-deleted users."""

    def get_queryset(self) -> UserQuerySet:
        """Return all users, including soft-deleted users."""
        return super().get_queryset()
