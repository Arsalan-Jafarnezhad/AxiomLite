"""Tests for accounts views."""

import pytest
from django.urls import reverse

from accounts.models import User


@pytest.mark.django_db
class TestAuthenticationViews:
    """Test authentication endpoints."""

    def test_sign_in_page(self, client):
        response = client.get(
            reverse("accounts:sign-in"),
        )

        assert response.status_code == 200

    def test_sign_up_page(self, client):
        response = client.get(
            reverse("accounts:sign-up"),
        )

        assert response.status_code == 200

    def test_account_requires_login(self, client):
        response = client.get(
            reverse("accounts:account"),
        )

        assert response.status_code == 302

    def test_account_detail_requires_login(self, client):
        response = client.get(
            reverse("accounts:account-detail"),
        )

        assert response.status_code == 302

    def test_account_edit_requires_login(self, client):
        response = client.get(
            reverse("accounts:account-edit"),
        )

        assert response.status_code == 302


@pytest.mark.django_db
class TestProfileView:
    """Test public profile pages."""

    def test_profile_page(self, client):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
            username="arsalan",
        )

        response = client.get(
            reverse(
                "accounts:profile",
                kwargs={"username": user.username},
            ),
        )

        assert response.status_code == 200

    def test_profile_not_found(self, client):
        response = client.get(
            reverse(
                "accounts:profile",
                kwargs={"username": "does-not-exist"},
            ),
        )

        assert response.status_code == 404