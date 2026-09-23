"""Tests for accounts models."""

from datetime import date

import pytest
from django.utils import timezone

from accounts.models import User


@pytest.mark.django_db
class TestUserModel:
    """Test User model behavior."""

    def test_string_representation(self):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
        )

        assert str(user) == "arsalan@example.com"

    def test_full_name(self):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
            first_name="Arsalan",
            last_name="Jafarnezhad",
        )

        assert user.full_name == "Arsalan Jafarnezhad"

    def test_short_name_prefers_first_name(self):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
            first_name="Arsalan",
            username="arsalan",
        )

        assert user.short_name == "Arsalan"

    def test_age(self):
        today = date.today()

        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
            born_date=date(
                today.year - 20,
                today.month,
                today.day,
            ),
        )

        assert user.age == 20

    def test_age_without_birth_date(self):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
        )

        assert user.age is None

    def test_verify_email(self):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
        )

        user.verify_email()
        user.refresh_from_db()

        assert user.is_verified is True
        assert user.is_email_verified is True
        assert user.email_verified_at is not None

    def test_verify_phone_number(self):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
        )

        user.verify_phone_number()
        user.refresh_from_db()

        assert user.is_phone_number_verified is True
        assert user.phone_number_verified_at is not None

    def test_deactivate(self):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
        )

        user.deactivate()

        assert user.is_active is False

    def test_activate(self):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
            is_active=False,
        )

        user.activate()

        assert user.is_active is True

    def test_update_last_activity(self):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
        )

        assert user.last_activity_at is None

        user.update_last_activity()
        user.refresh_from_db()

        assert user.last_activity_at is not None

    def test_soft_delete(self):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
        )

        user.delete()
        user.refresh_from_db()

        assert user.is_deleted is True
        assert user.deleted_at is not None

    def test_restore(self):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
        )

        user.delete()
        user.restore()
        user.refresh_from_db()

        assert user.is_deleted is False
        assert user.deleted_at is None