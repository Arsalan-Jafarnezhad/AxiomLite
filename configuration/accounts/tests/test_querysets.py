"""Tests for accounts querysets."""

import pytest

from accounts.models import User


@pytest.fixture
def users(db):
    """Create a representative set of users."""
    return {
        "active": User.objects.create_user(
            "active@example.com",
            "password123",
            is_active=True,
        ),
        "inactive": User.objects.create_user(
            "inactive@example.com",
            "password123",
            is_active=False,
        ),
        "verified": User.objects.create_user(
            "verified@example.com",
            "password123",
            is_verified=True,
        ),
        "unverified": User.objects.create_user(
            "unverified@example.com",
            "password123",
            is_verified=False,
        ),
    }


@pytest.mark.django_db
class TestUserQuerySet:
    """Test collection-level user operations."""

    def test_active(self, users):
        queryset = User.objects.active()

        assert users["active"] in queryset
        assert users["inactive"] not in queryset

    def test_inactive(self, users):
        queryset = User.objects.inactive()

        assert users["inactive"] in queryset
        assert users["active"] not in queryset

    def test_verified(self, users):
        queryset = User.objects.verified()

        assert users["verified"] in queryset
        assert users["unverified"] not in queryset

    def test_unverified(self, users):
        queryset = User.objects.unverified()

        assert users["unverified"] in queryset
        assert users["verified"] not in queryset

    def test_by_username_is_case_insensitive(self):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
            username="Arsalan",
        )

        assert User.objects.by_username("ARSALAN").get() == user

    def test_by_email_is_case_insensitive(self):
        user = User.objects.create_user(
            "Arsalan@example.com",
            "password123",
        )

        assert User.objects.by_email(
            "arsalan@example.com",
        ).get() == user

    def test_get_by_username_returns_user(self):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
            username="arsalan",
        )

        assert User.objects.get_by_username("ARSALAN") == user

    def test_get_by_username_returns_none(self):
        assert User.objects.get_by_username(
            "does-not-exist",
        ) is None

    def test_searchable(self):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
            first_name="Arsalan",
        )

        assert user in User.objects.searchable("arsalan")

    def test_empty_search_returns_none(self):
        assert not User.objects.searchable(" ").exists()

    def test_deleted_users_are_hidden(self):
        user = User.objects.create_user(
            "deleted@example.com",
            "password123",
        )

        user.delete()

        assert not User.objects.filter(pk=user.pk).exists()