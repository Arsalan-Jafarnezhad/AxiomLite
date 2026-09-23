"""Tests for accounts forms."""

import pytest

from accounts.forms.account import AccountForm
from accounts.forms.authentication import (
    AccountLoginForm,
    AccountSignUpForm,
)
from accounts.forms.profile import ProfileForm
from accounts.models import User


@pytest.mark.django_db
class TestAccountSignUpForm:
    """Test account registration form."""

    def test_valid_data(self):
        form = AccountSignUpForm(
            data={
                "email": "arsalan@example.com",
                "password1": "StrongPassword123!",
                "password2": "StrongPassword123!",
            },
        )
        assert form.is_valid(), form.errors


@pytest.mark.django_db
class TestAccountForm:
    """Test account editing form."""

    def test_form_uses_user_instance(self):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
        )

        form = AccountForm(instance=user)

        assert form.instance == user


@pytest.mark.django_db
class TestProfileForm:
    """Test profile form."""

    def test_form_uses_profile_instance(self):
        user = User.objects.create_user(
            "arsalan@example.com",
            "password123",
        )

        form = ProfileForm(
            instance=user.profile,
        )

        assert form.instance == user.profile


class TestAccountLoginForm:
    """Test authentication form construction."""

    def test_form_can_be_constructed(self):
        form = AccountLoginForm()

        assert form is not None