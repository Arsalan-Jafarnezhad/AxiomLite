"""
Comprehensive test suite for the accounts app.

Covers:
- UserManager (create_user, create_superuser, normalization)
- User model (properties, verification, lifecycle, soft-delete)
- UserQuerySet (verified, staff, by_username, get_by_username)
- Profile model (name, points, level, progress, completion, soft-delete)
- Address model (default-address constraint, ordering, string)
- Rank model (validation, ordering, unique priority, string)
- BaseModel (public_id, timestamps)
- SoftDeleteModel / SoftDeleteQuerySet (delete, restore, alive, deleted, hard_delete)
- AccountForm / AccountSignUpForm / AccountLoginForm / ProfileForm
- Account views (sign-in, sign-up, sign-out, account, account-edit, account-detail)
- Profile views (public, private, 404)
- Utility helpers (ids, ip, upload_paths)
- Signals (auto-create Profile on User creation)
"""

from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase, RequestFactory
from django.urls import reverse

from accounts.forms import (
    AccountForm,
    AccountLoginForm,
    AccountSignUpForm,
    ProfileForm,
)
from accounts.models import Address, Profile, Rank
from accounts.models.soft_delete import SoftDeleteModel
from accounts.querysets import UserQuerySet
from accounts.utils.ids import generate_public_id, generate_slug
from accounts.utils.ip import get_country_by_ip, get_user_ip_address
from accounts.utils.upload_paths import (
    profile_image_upload_path,
    rank_image_upload_path,
    safe_extension,
)

User = get_user_model()


# ─────────────────────────────────────────────────────────────────────────────
# UserManager
# ─────────────────────────────────────────────────────────────────────────────


class UserManagerTests(TestCase):
    """Tests for UserManager.create_user / create_superuser."""

    def test_create_user_requires_email(self):
        with self.assertRaisesMessage(ValueError, "Email required"):
            User.objects.create_user("", "password123")

    def test_create_user_normalizes_email(self):
        user = User.objects.create_user("Jane.Doe@Example.COM", "password123")
        self.assertEqual(user.email, "Jane.Doe@example.com")

    def test_create_user_generates_username_from_email(self):
        user = User.objects.create_user("Jane.Doe@Example.COM", "password123")
        self.assertEqual(user.username, "janedoe")

    def test_create_user_sets_password(self):
        user = User.objects.create_user("user@example.com", "password123")
        self.assertTrue(user.check_password("password123"))
        self.assertFalse(user.check_password("wrong-password"))

    def test_create_user_with_extra_fields(self):
        user = User.objects.create_user(
            "extra@example.com",
            "password123",
            first_name="Ada",
            last_name="Lovelace",
            is_verified=True,
        )
        self.assertEqual(user.first_name, "Ada")
        self.assertEqual(user.last_name, "Lovelace")
        self.assertTrue(user.is_verified)

    def test_create_user_auto_creates_profile(self):
        user = User.objects.create_user("profile@example.com", "password123")
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_create_superuser_defaults(self):
        admin = User.objects.create_superuser("admin@example.com", "password123")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)

    def test_create_superuser_with_extra_fields(self):
        admin = User.objects.create_superuser(
            "admin2@example.com",
            "password123",
            first_name="Super",
            is_verified=True,
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.first_name, "Super")
        self.assertTrue(admin.is_verified)


# ─────────────────────────────────────────────────────────────────────────────
# User model
# ─────────────────────────────────────────────────────────────────────────────


class UserModelTests(TestCase):
    """Tests for the User model's properties and lifecycle methods."""

    def setUp(self):
        self.user = User.objects.create_user(
            "person@example.com",
            "password123",
            first_name="Ada",
            last_name="Lovelace",
            born_date=date.today().replace(year=date.today().year - 30),
        )

    def test_full_name(self):
        self.assertEqual(self.user.full_name, "Ada Lovelace")

    def test_full_name_with_no_names(self):
        user = User.objects.create_user("noname@example.com", "password123")
        self.assertEqual(user.full_name, "")

    def test_short_name(self):
        self.assertEqual(self.user.short_name, "Ada")

    def test_short_name_falls_back_to_username(self):
        user = User.objects.create_user("fallback@example.com", "password123")
        self.assertEqual(user.short_name, user.username)

    def test_short_name_falls_back_to_email(self):
        user = User.objects.create_user("email@example.com", "password123")
        user.username = ""
        user.first_name = ""
        user.save()
        self.assertEqual(user.short_name, user.email)

    def test_age(self):
        self.assertEqual(self.user.age, 30)

    def test_age_with_no_born_date(self):
        user = User.objects.create_user("noage@example.com", "password123")
        self.assertIsNone(user.age)

    def test_is_email_verified_initially_false(self):
        self.assertFalse(self.user.is_email_verified)

    def test_verify_email(self):
        self.user.verify_email()
        self.assertTrue(self.user.is_email_verified)
        self.assertTrue(self.user.is_verified)
        self.assertIsNotNone(self.user.email_verified_at)

    def test_is_phone_number_verified_initially_false(self):
        self.assertFalse(self.user.is_phone_number_verified)

    def test_verify_phone_number(self):
        self.user.verify_phone_number()
        self.assertTrue(self.user.is_phone_number_verified)
        self.assertIsNotNone(self.user.phone_number_verified_at)

    def test_update_last_activity(self):
        self.assertIsNone(self.user.last_activity_at)
        self.user.update_last_activity()
        self.assertIsNotNone(self.user.last_activity_at)

    def test_deactivate(self):
        self.assertTrue(self.user.is_active)
        self.user.deactivate()
        self.assertFalse(self.user.is_active)

    def test_activate(self):
        self.user.deactivate()
        self.assertFalse(self.user.is_active)
        self.user.activate()
        self.assertTrue(self.user.is_active)

    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), "Ada Lovelace")

    def test_get_short_name(self):
        self.assertEqual(self.user.get_short_name(), "Ada")

    def test_is_official_with_official_group(self):
        Group.objects.create(name="Manager").user_set.add(self.user)
        self.assertTrue(self.user.is_official)

    def test_is_official_with_non_official_group(self):
        Group.objects.create(name="Regular").user_set.add(self.user)
        self.assertFalse(self.user.is_official)

    def test_is_official_with_no_groups(self):
        self.assertFalse(self.user.is_official)

    def test_get_phone_number_country_short_name(self):
        user = User.objects.create_user(
            "phone@example.com", "password123", phone_number="+14155552671"
        )
        self.assertEqual(user.get_phone_number_country_short_name(), "us")

    def test_get_phone_number_country_short_name_with_no_phone(self):
        self.assertIsNone(self.user.get_phone_number_country_short_name())

    def test_get_phone_number_country_short_name_with_invalid_phone(self):
        user = User.objects.create_user(
            "invalid@example.com", "password123", phone_number="+99999999999"
        )
        self.assertIsNone(user.get_phone_number_country_short_name())

    def test_save_generates_username_if_blank(self):
        user = User(email="gen@example.com")
        user.set_password("password123")
        user.save()
        self.assertEqual(user.username, "gen")

    def test_generate_unique_username(self):
        User.objects.create_user("unique@example.com", "password123")
        user2 = User.objects.create_user("unique2@example.com", "password123")
        self.assertNotEqual(user2.username, "unique")

    def test_public_id_is_generated(self):
        self.assertTrue(self.user.public_id)
        self.assertEqual(len(self.user.public_id), 32)

    def test_created_at_and_updated_at_are_set(self):
        self.assertIsNotNone(self.user.created_at)
        self.assertIsNotNone(self.user.updated_at)

    def test_str_returns_email(self):
        self.assertEqual(str(self.user), "person@example.com")

    def test_username_is_case_insensitive_unique(self):
        user1 = User.objects.create_user("case@example.com", "password123")
        user2 = User(email="case2@example.com", username="CASE")
        user2.set_password("password123")
        with self.assertRaises(Exception):
            user2.save()


# ─────────────────────────────────────────────────────────────────────────────
# UserQuerySet
# ─────────────────────────────────────────────────────────────────────────────


class UserQuerySetTests(TestCase):
    """Tests for UserQuerySet helper methods."""

    def setUp(self):
        self.verified = User.objects.create_user(
            "verified@example.com", "password123", is_verified=True
        )
        self.unverified = User.objects.create_user(
            "unverified@example.com", "password123"
        )
        self.staff = User.objects.create_user(
            "staff@example.com", "password123", is_staff=True
        )
        self.non_staff = User.objects.create_user("nonstaff@example.com", "password123")

    def test_verified(self):
        self.assertIn(self.verified, User.objects.verified())
        self.assertNotIn(self.unverified, User.objects.verified())

    def test_staff(self):
        self.assertIn(self.staff, User.objects.staff())
        self.assertNotIn(self.non_staff, User.objects.staff())

    def test_by_username_case_insensitive(self):
        qs = User.objects.by_username(self.verified.username.upper())
        self.assertIn(self.verified, qs)

    def test_get_by_username_case_insensitive(self):
        self.assertIs(
            User.objects.get_by_username(self.verified.username.upper()), self.verified
        )

    def test_get_by_username_returns_none_when_missing(self):
        self.assertIsNone(User.objects.get_by_username("nonexistent"))


# ─────────────────────────────────────────────────────────────────────────────
# Profile model
# ─────────────────────────────────────────────────────────────────────────────


class ProfileModelTests(TestCase):
    """Tests for the Profile model."""

    def setUp(self):
        self.user = User.objects.create_user("profile@example.com", "password123")
        self.profile = self.user.profile

    def test_name_falls_back_to_email(self):
        self.assertEqual(self.profile.name, self.user.email)

    def test_name_uses_display_name(self):
        self.profile.display_name = "Public name"
        self.assertEqual(self.profile.name, "Public name")

    def test_name_falls_back_to_full_name(self):
        self.user.first_name = "Ada"
        self.user.last_name = "Lovelace"
        self.user.save()
        self.assertEqual(self.profile.name, "Ada Lovelace")

    def test_avatar_url_empty_when_no_avatar(self):
        self.assertEqual(self.profile.avatar_url, "")

    def test_update_level(self):
        self.profile.points = 250
        self.profile.update_level()
        self.assertEqual(self.profile.level, 2)

    def test_update_level_with_zero_points(self):
        self.profile.points = 0
        self.profile.update_level()
        self.assertEqual(self.profile.level, 0)

    def test_add_points(self):
        self.profile.add_points(100)
        self.assertEqual(self.profile.points, 100)

    def test_add_points_ignores_nonpositive(self):
        self.profile.add_points(0)
        self.assertEqual(self.profile.points, 0)
        self.profile.add_points(-10)
        self.assertEqual(self.profile.points, 0)

    def test_remove_points(self):
        self.profile.add_points(100)
        self.profile.remove_points(40)
        self.assertEqual(self.profile.points, 60)

    def test_remove_points_ignores_nonpositive(self):
        self.profile.add_points(100)
        self.profile.remove_points(0)
        self.assertEqual(self.profile.points, 100)

    def test_remove_points_cannot_go_negative(self):
        self.profile.add_points(50)
        self.profile.remove_points(1000)
        self.assertEqual(self.profile.points, 0)

    def test_current_points(self):
        self.profile.points = 250
        self.profile.update_level()
        self.assertGreaterEqual(self.profile.current_points, 0)

    def test_needed_points(self):
        self.assertGreater(self.profile.needed_points, 0)

    def test_level_points(self):
        self.profile.points = 250
        self.profile.update_level()
        self.assertGreater(self.profile.level_points, 0)

    def test_progress_percent(self):
        self.profile.points = 250
        self.profile.update_level()
        self.assertGreaterEqual(self.profile.progress_percent, 0)
        self.assertLessEqual(self.profile.progress_percent, 100)

    def test_completion_percent(self):
        self.assertGreaterEqual(self.profile.completion_percent, 0)
        self.assertLessEqual(self.profile.completion_percent, 100)

    def test_missing_profile_items(self):
        missing = self.profile.missing_profile_items
        self.assertIn("Avatar", missing)
        self.assertIn("Display Name", missing)
        self.assertIn("Biography", missing)
        self.assertIn("First Name", missing)
        self.assertIn("Last Name", missing)
        self.assertIn("Phone Number", missing)
        self.assertIn("Phone Verification", missing)
        self.assertIn("Birth Date", missing)
        self.assertIn("Gender", missing)
        self.assertIn("Email Verification", missing)

    def test_missing_profile_items_when_complete(self):
        self.profile.avatar = "test-avatar.png"
        self.profile.display_name = "Test"
        self.profile.biography = "Bio"
        self.user.first_name = "First"
        self.user.last_name = "Last"
        self.user.phone_number = "+14155552671"
        self.user.born_date = date.today()
        self.user.gender = 1
        self.user.verify_email()
        self.user.verify_phone_number()
        self.user.save()
        self.profile.save()
        missing = self.profile.missing_profile_items
        self.assertEqual(missing, [])

    def test_str_returns_name(self):
        self.assertEqual(str(self.profile), self.user.email)

    def test_meta_ordering(self):
        p1 = Profile.objects.create(user=self.user)
        p2 = Profile.objects.create(
            user=User.objects.create_user("p2@example.com", "password123")
        )
        self.assertEqual(list(Profile.objects.order_by("-created_at"))[0].pk, p2.pk)


# ─────────────────────────────────────────────────────────────────────────────
# Address model
# ─────────────────────────────────────────────────────────────────────────────


class AddressModelTests(TestCase):
    """Tests for the Address model."""

    def setUp(self):
        self.user = User.objects.create_user("address@example.com", "password123")

    def _make_address(self, **kwargs):
        values = dict(
            receiver_name="A User",
            phone_number="+14155552671",
            country="US",
            province="CA",
            city="SF",
            postal_code="94105",
            address="Main St",
        )
        values.update(kwargs)
        return Address.objects.create(user=self.user, **values)

    def test_only_one_default_address_per_user(self):
        first = self._make_address(title="Home", is_default=True)
        second = self._make_address(title="Office", is_default=True)
        first.refresh_from_db()
        self.assertFalse(first.is_default)
        self.assertTrue(second.is_default)

    def test_str_returns_title_and_receiver(self):
        address = self._make_address(title="Office")
        self.assertEqual(str(address), "Office — A User")

    def test_meta_ordering(self):
        self._make_address(title="A", is_default=False)
        self._make_address(title="B", is_default=True)
        addresses = list(Address.objects.all())
        self.assertEqual(addresses[0].title, "B")

    def test_public_id_is_generated(self):
        address = self._make_address(title="Test")
        self.assertTrue(address.public_id)
        self.assertEqual(len(address.public_id), 32)

    def test_created_at_and_updated_at_are_set(self):
        address = self._make_address(title="Test")
        self.assertIsNotNone(address.created_at)
        self.assertIsNotNone(address.updated_at)


# ─────────────────────────────────────────────────────────────────────────────
# Rank model
# ─────────────────────────────────────────────────────────────────────────────


class RankModelTests(TestCase):
    """Tests for the Rank model."""

    def test_str_returns_name(self):
        rank = Rank.objects.create(name="Gold", activation_level=2, priority=5)
        self.assertEqual(str(rank), "Gold")

    def test_name_min_length_validation(self):
        with self.assertRaises(ValidationError):
            Rank(name="X", activation_level=0).full_clean()

    def test_name_min_length_valid(self):
        rank = Rank(name="Gold", activation_level=2, priority=5)
        rank.full_clean()

    def test_activation_level_min_value_validation(self):
        with self.assertRaises(ValidationError):
            Rank(name="Gold", activation_level=-1).full_clean()

    def test_priority_min_value_validation(self):
        with self.assertRaises(ValidationError):
            Rank(name="Gold", activation_level=0, priority=-1).full_clean()

    def test_meta_ordering_by_priority(self):
        Rank.objects.create(name="Low", activation_level=1, priority=1)
        Rank.objects.create(name="High", activation_level=2, priority=10)
        ranks = list(Rank.objects.all())
        self.assertEqual(ranks[0].name, "High")
        self.assertEqual(ranks[1].name, "Low")

    def test_unique_priority_constraint(self):
        Rank.objects.create(name="Gold", activation_level=2, priority=5)
        with self.assertRaises(Exception):
            Rank.objects.create(name="Silver", activation_level=1, priority=5)

    def test_public_id_is_generated(self):
        rank = Rank.objects.create(name="Gold", activation_level=2, priority=5)
        self.assertTrue(rank.public_id)
        self.assertEqual(len(rank.public_id), 32)

    def test_created_at_and_updated_at_are_set(self):
        rank = Rank.objects.create(name="Gold", activation_level=2, priority=5)
        self.assertIsNotNone(rank.created_at)
        self.assertIsNotNone(rank.updated_at)


# ─────────────────────────────────────────────────────────────────────────────
# BaseModel
# ─────────────────────────────────────────────────────────────────────────────


class BaseModelTests(TestCase):
    """Tests for the BaseModel abstract class."""

    def test_public_id_is_generated(self):
        user = User.objects.create_user("base@example.com", "password123")
        self.assertTrue(user.public_id)
        self.assertEqual(len(user.public_id), 32)

    def test_public_id_is_unique(self):
        user1 = User.objects.create_user("base1@example.com", "password123")
        user2 = User.objects.create_user("base2@example.com", "password123")
        self.assertNotEqual(user1.public_id, user2.public_id)

    def test_created_at_and_updated_at_are_set(self):
        user = User.objects.create_user("base3@example.com", "password123")
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)


# ─────────────────────────────────────────────────────────────────────────────
# SoftDeleteModel / SoftDeleteQuerySet
# ─────────────────────────────────────────────────────────────────────────────


class SoftDeleteTests(TestCase):
    """Tests for SoftDeleteModel and SoftDeleteQuerySet."""

    def setUp(self):
        self.user = User.objects.create_user("soft@example.com", "password123")
        self.profile = self.user.profile

    def test_soft_delete_hides_object(self):
        self.profile.delete()
        self.assertFalse(Profile.objects.filter(pk=self.profile.pk).exists())

    def test_soft_delete_sets_is_deleted(self):
        self.profile.delete()
        self.assertTrue(
            Profile.all_objects.filter(pk=self.profile.pk, is_deleted=True).exists()
        )

    def test_soft_delete_sets_deleted_at(self):
        self.profile.delete()
        deleted = Profile.all_objects.get(pk=self.profile.pk)
        self.assertIsNotNone(deleted.deleted_at)

    def test_restore_returns_object(self):
        self.profile.delete()
        self.profile.restore()
        self.assertTrue(Profile.objects.filter(pk=self.profile.pk).exists())

    def test_restore_clears_is_deleted(self):
        self.profile.delete()
        self.profile.restore()
        self.assertFalse(Profile.all_objects.get(pk=self.profile.pk).is_deleted)

    def test_restore_clears_deleted_at(self):
        self.profile.delete()
        self.profile.restore()
        self.assertIsNone(Profile.all_objects.get(pk=self.profile.pk).deleted_at)

    def test_alive_queryset(self):
        self.profile.delete()
        self.assertFalse(self.profile.pk in [p.pk for p in Profile.objects.alive()])

    def test_deleted_queryset(self):
        self.profile.delete()
        self.assertTrue(self.profile.pk in [p.pk for p in Profile.objects.deleted()])

    def test_hard_delete(self):
        self.profile.delete()
        Profile.objects.hard_delete()
        self.assertFalse(Profile.all_objects.filter(pk=self.profile.pk).exists())

    def test_user_soft_delete(self):
        self.user.delete()
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
        self.assertTrue(
            User.all_objects.filter(pk=self.user.pk, is_deleted=True).exists()
        )

    def test_user_restore(self):
        self.user.delete()
        self.user.restore()
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())


# ─────────────────────────────────────────────────────────────────────────────
# Forms
# ─────────────────────────────────────────────────────────────────────────────


class AccountSignUpFormTests(TestCase):
    """Tests for AccountSignUpForm."""

    def test_signup_validates_passwords_match(self):
        form = AccountSignUpForm(
            data={
                "email": "NEW@EXAMPLE.COM",
                "password1": "Strong-pass-123",
                "password2": "different",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_signup_validates_duplicate_email(self):
        User.objects.create_user("taken@example.com", "password123")
        form = AccountSignUpForm(
            data={
                "email": "TAKEN@example.com",
                "password1": "Strong-pass-123",
                "password2": "Strong-pass-123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_signup_email_is_case_insensitive(self):
        User.objects.create_user("case@example.com", "password123")
        form = AccountSignUpForm(
            data={
                "email": "CASE@example.com",
                "password1": "Strong-pass-123",
                "password2": "Strong-pass-123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_signup_validates_password_strength(self):
        form = AccountSignUpForm(
            data={
                "email": "weak@example.com",
                "password1": "123",
                "password2": "123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_signup_save_creates_user(self):
        form = AccountSignUpForm(
            data={
                "email": "new@example.com",
                "password1": "Strong-pass-123",
                "password2": "Strong-pass-123",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(user.check_password("Strong-pass-123"))
        self.assertEqual(user.email, "new@example.com")

    def test_signup_save_normalizes_email(self):
        form = AccountSignUpForm(
            data={
                "email": "NEW@EXAMPLE.COM",
                "password1": "Strong-pass-123",
                "password2": "Strong-pass-123",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.email, "new@example.com")


class AccountFormTests(TestCase):
    """Tests for AccountForm."""

    def setUp(self):
        self.user = User.objects.create_user("account@example.com", "password123")

    def test_fieldsets(self):
        form = AccountForm(instance=self.user)
        self.assertEqual(len(form.fieldsets), 2)
        self.assertEqual(form.fieldsets[0]["name"], "Personal Information")
        self.assertEqual(form.fieldsets[1]["name"], "Account Information")

    def test_clean_email_rejects_duplicate(self):
        User.objects.create_user("other@example.com", "password123")
        form = AccountForm(
            instance=self.user,
            data={
                "first_name": "",
                "last_name": "",
                "email": "other@example.com",
                "username": self.user.username,
                "gender": "",
                "born_date": "",
                "phone_number": "",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_clean_email_allows_own_email(self):
        form = AccountForm(
            instance=self.user,
            data={
                "first_name": "",
                "last_name": "",
                "email": "account@example.com",
                "username": self.user.username,
                "gender": "",
                "born_date": "",
                "phone_number": "",
            },
        )
        self.assertTrue(form.is_valid(), form.errors)


class AccountLoginFormTests(TestCase):
    """Tests for AccountLoginForm."""

    def test_fieldsets(self):
        form = AccountLoginForm()
        self.assertEqual(len(form.fieldsets), 1)
        self.assertIn("login", form.fieldsets[0]["fields"])
        self.assertIn("password", form.fieldsets[0]["fields"])

    def test_login_field_label(self):
        form = AccountLoginForm()
        self.assertEqual(form.fields["login"].label, "Email Address")

    def test_password_field_label(self):
        form = AccountLoginForm()
        self.assertEqual(form.fields["password"].label, "Password")


class ProfileFormTests(TestCase):
    """Tests for ProfileForm."""

    def setUp(self):
        self.user = User.objects.create_user("profileform@example.com", "password123")

    def test_fieldsets(self):
        form = ProfileForm(instance=self.user.profile)
        self.assertEqual(len(form.fieldsets), 1)
        self.assertEqual(form.fieldsets[0]["name"], "Profile Information")

    def test_fields(self):
        form = ProfileForm(instance=self.user.profile)
        self.assertIn("avatar", form.fields)
        self.assertIn("display_name", form.fields)
        self.assertIn("biography", form.fields)
        self.assertIn("is_private", form.fields)


# ─────────────────────────────────────────────────────────────────────────────
# Views
# ─────────────────────────────────────────────────────────────────────────────


class AccountViewTests(TestCase):
    """Tests for account views."""

    def setUp(self):
        self.user = User.objects.create_user("viewer@example.com", "password123")

    def test_urls_resolve(self):
        self.assertEqual(reverse("accounts:sign-in"), "/accounts/sign-in/")
        self.assertEqual(reverse("accounts:sign-up"), "/accounts/sign-up/")
        self.assertEqual(reverse("accounts:sign-out"), "/accounts/sign-out/")
        self.assertEqual(reverse("accounts:account"), "/accounts/account/")
        self.assertEqual(reverse("accounts:account-edit"), "/accounts/account/edit/")
        self.assertEqual(
            reverse("accounts:account-detail"), "/accounts/account/detail/"
        )

    def test_index_redirects_to_account(self):
        response = self.client.get(reverse("accounts:index"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("accounts:account"))

    def test_account_requires_login(self):
        response = self.client.get(reverse("accounts:account"))
        self.assertEqual(response.status_code, 302)

    def test_account_returns_200_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:account"))
        self.assertEqual(response.status_code, 200)

    def test_account_detail_returns_200_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:account-detail"))
        self.assertEqual(response.status_code, 200)

    def test_account_edit_requires_login(self):
        response = self.client.get(reverse("accounts:account-edit"))
        self.assertEqual(response.status_code, 302)

    def test_account_edit_returns_200_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:account-edit"))
        self.assertEqual(response.status_code, 200)

    def test_sign_in_returns_200(self):
        response = self.client.get(reverse("accounts:sign-in"))
        self.assertEqual(response.status_code, 200)

    def test_sign_up_returns_200(self):
        response = self.client.get(reverse("accounts:sign-up"))
        self.assertEqual(response.status_code, 200)

    def test_sign_up_redirects_when_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:sign-up"))
        self.assertEqual(response.status_code, 302)

    def test_sign_out_logs_out(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:sign-out"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["level"], "success")
        self.assertNotEqual(response.json()["message"], "")

    def test_sign_out_allows_anonymous(self):
        response = self.client.post(reverse("accounts:sign-out"))
        self.assertEqual(response.status_code, 200)


class ProfileViewTests(TestCase):
    """Tests for profile views."""

    def setUp(self):
        self.user = User.objects.create_user("profileview@example.com", "password123")

    def test_profile_public_page(self):
        response = self.client.get(
            reverse("accounts:profile", args=[self.user.username])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile/public.html")

    def test_profile_private_page(self):
        self.user.profile.is_private = True
        self.user.profile.save()
        response = self.client.get(
            reverse("accounts:profile", args=[self.user.username])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile/secure.html")

    def test_profile_404_for_missing_user(self):
        response = self.client.get(reverse("accounts:profile", args=["missing"]))
        self.assertEqual(response.status_code, 404)

    def test_profile_is_own_profile_context(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("accounts:profile", args=[self.user.username])
        )
        self.assertTrue(response.context["is_own_profile"])

    def test_profile_not_own_profile_context(self):
        other = User.objects.create_user("other@example.com", "password123")
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:profile", args=[other.username]))
        self.assertFalse(response.context["is_own_profile"])


# ─────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────────────────────────────────────


class UtilityTests(TestCase):
    """Tests for utility helper functions."""

    def test_generate_public_id_length(self):
        self.assertEqual(len(generate_public_id()), 32)

    def test_generate_public_id_is_unique(self):
        self.assertNotEqual(generate_public_id(), generate_public_id())

    def test_generate_slug_format(self):
        slug = generate_slug()
        self.assertEqual(len(slug), 36)
        self.assertEqual(slug.count("-"), 4)

    def test_get_user_ip_address_with_x_forwarded_for(self):
        request = RequestFactory().get(
            "/", HTTP_X_FORWARDED_FOR="203.0.113.1, 10.0.0.1"
        )
        self.assertEqual(get_user_ip_address(request), "203.0.113.1")

    def test_get_user_ip_address_with_remote_addr(self):
        request = RequestFactory().get("/")
        request.META["REMOTE_ADDR"] = "192.168.1.1"
        self.assertEqual(get_user_ip_address(request), "192.168.1.1")

    def test_get_user_ip_address_returns_none_when_no_ip(self):
        request = RequestFactory().get("/")
        request.META.pop("REMOTE_ADDR", None)
        self.assertIsNone(get_user_ip_address(request))

    def test_get_country_by_ip_with_none(self):
        self.assertIsNone(get_country_by_ip(None))

    def test_get_country_by_ip_with_empty_string(self):
        self.assertIsNone(get_country_by_ip(""))

    def test_get_country_by_ip_with_invalid_ip(self):
        self.assertIsNone(get_country_by_ip("not-an-ip"))

    def test_get_country_by_ip_with_valid_ip(self):
        # Currently stubbed to always return None
        self.assertIsNone(get_country_by_ip("203.0.113.1"))

    def test_safe_extension_with_known_extension(self):
        self.assertEqual(safe_extension("photo.png"), ".png")

    def test_safe_extension_with_unknown_extension(self):
        self.assertEqual(safe_extension("photo.unknownext"), ".jpg")

    def test_profile_image_upload_path(self):
        user = User.objects.create_user("upload@example.com", "password123")
        path = profile_image_upload_path(user.profile, "avatar.png")
        self.assertTrue(path.startswith("accounts/profiles/"))
        self.assertTrue(path.endswith(".png"))

    def test_rank_image_upload_path(self):
        rank = Rank(name="Gold", activation_level=1, priority=1)
        path = rank_image_upload_path(rank, "rank.jpg")
        self.assertTrue(path.startswith("accounts/ranks/"))
        self.assertTrue(path.endswith(".jpg"))
