"""Tests for accounts managers."""

import pytest

from accounts.models import User


@pytest.mark.django_db
class TestUserManager:
    """Test UserManager behavior."""

    def test_create_user_requires_email(self):
        with pytest.raises(ValueError, match="Email required"):
            User.objects.create_user(
                "",
                "password123",
            )

    def test_create_user_normalizes_email(self):
        user = User.objects.create_user(
            "Jane.Doe@EXAMPLE.COM",
            "password123",
        )

        assert user.email == "Jane.Doe@example.com"

    def test_create_user_sets_password(self):
        user = User.objects.create_user(
            "jane@example.com",
            "password123",
        )

        assert user.check_password("password123")

    def test_create_user_without_password_uses_unusable_password(self):
        user = User.objects.create_user(
            "jane@example.com",
        )

        assert not user.has_usable_password()

    def test_create_user_generates_username(self):
        user = User.objects.create_user(
            "Jane.Doe@example.com",
            "password123",
        )

        assert user.username == "jane-doe"

    def test_create_superuser_sets_required_flags(self):
        user = User.objects.create_superuser(
            "admin@example.com",
            "password123",
        )

        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.is_active is True

    def test_create_superuser_requires_password(self):
        with pytest.raises(
            ValueError,
            match="Superuser password required",
        ):
            User.objects.create_superuser(
                "admin@example.com",
                "",
            )

    def test_create_superuser_rejects_non_staff(self):
        with pytest.raises(
            ValueError,
            match="is_staff=True",
        ):
            User.objects.create_superuser(
                "admin@example.com",
                "password123",
                is_staff=False,
            )

    def test_create_superuser_rejects_non_superuser(self):
        with pytest.raises(
            ValueError,
            match="is_superuser=True",
        ):
            User.objects.create_superuser(
                "admin@example.com",
                "password123",
                is_superuser=False,
            )

    def test_all_objects_includes_deleted_users(self):
        user = User.objects.create_user(
            "deleted@example.com",
            "password123",
        )

        user.delete()

        assert not User.objects.filter(pk=user.pk).exists()
        assert User.all_objects.filter(pk=user.pk).exists()