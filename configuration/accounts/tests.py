from datetime import date
from unittest.mock import patch

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase, RequestFactory
from django.urls import reverse

from accounts.forms import AccountForm, AccountSignUpForm, ProfileForm
from accounts.models import Address, Profile, Rank
from accounts.models.soft_delete import SoftDeleteModel
from accounts.querysets import UserQuerySet
from accounts.utils.ids import generate_public_id, generate_slug
from accounts.utils.ip import get_country_by_ip, get_user_ip_address
from accounts.utils.upload_paths import profile_image_upload_path, rank_image_upload_path, safe_extension

User = get_user_model()


class UserManagerAndModelTests(TestCase):
    def test_create_user_requires_email_and_normalizes_username(self):
        with self.assertRaisesMessage(ValueError, "Email required"):
            User.objects.create_user("", "password123")
        user = User.objects.create_user("Jane.Doe@Example.COM", "password123")
        self.assertEqual(user.email, "Jane.Doe@example.com")
        self.assertEqual(user.username, "janedoe")
        self.assertTrue(user.check_password("password123"))
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_superuser_defaults_and_queryset_helpers(self):
        admin = User.objects.create_superuser("admin@example.com", "password123")
        verified = User.objects.create_user("verified@example.com", "password123", is_verified=True)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertIn(verified, User.objects.verified())
        self.assertIn(admin, User.objects.staff())
        self.assertIs(User.objects.get_by_username(verified.username.upper()), verified)
        self.assertIsNone(User.objects.get_by_username("missing"))

    def test_user_properties_verification_activity_and_lifecycle(self):
        user = User.objects.create_user(
            "person@example.com", "password123", first_name="Ada", last_name="Lovelace",
            born_date=date.today().replace(year=date.today().year - 30),
        )
        self.assertEqual(user.full_name, "Ada Lovelace")
        self.assertEqual(user.short_name, "Ada")
        self.assertEqual(user.age, 30)
        self.assertFalse(user.is_email_verified)
        user.verify_email()
        user.verify_phone_number()
        user.update_last_activity()
        user.deactivate()
        self.assertTrue(user.is_email_verified)
        self.assertTrue(user.is_phone_number_verified)
        self.assertIsNotNone(user.last_activity_at)
        self.assertFalse(user.is_active)
        user.activate()
        self.assertTrue(user.is_active)

    def test_official_group_and_phone_country(self):
        user = User.objects.create_user("official@example.com", "password123", phone_number="+14155552671")
        self.assertEqual(user.get_phone_number_country_short_name(), "us")
        Group.objects.create(name="Manager").user_set.add(user)
        self.assertTrue(user.is_official)


class ProfileAndSoftDeleteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("profile@example.com", "password123")
        self.profile = self.user.profile

    def test_profile_name_and_progress_properties(self):
        self.assertEqual(self.profile.name, self.user.email)
        self.profile.display_name = "Public name"
        self.profile.points = 250
        self.profile.update_level()
        self.assertEqual(self.profile.name, "Public name")
        self.assertEqual(self.profile.level, 2)
        self.assertGreater(self.profile.needed_points, 0)
        self.assertGreaterEqual(self.profile.progress_percent, 0)
        self.assertIn("Biography", self.profile.missing_profile_items)
        self.assertGreaterEqual(self.profile.completion_percent, 0)

    def test_add_and_remove_points_ignore_nonpositive_amounts(self):
        self.profile.add_points(100)
        self.assertEqual(self.profile.points, 100)
        self.profile.add_points(0)
        self.profile.remove_points(40)
        self.assertEqual(self.profile.points, 60)
        self.profile.remove_points(1000)
        self.assertEqual(self.profile.points, 0)

    def test_soft_delete_hides_object_but_restore_returns_it(self):
        self.profile.delete()
        self.assertFalse(Profile.objects.filter(pk=self.profile.pk).exists())
        self.assertTrue(Profile.all_objects.filter(pk=self.profile.pk, is_deleted=True).exists())
        self.profile.restore()
        self.assertTrue(Profile.objects.filter(pk=self.profile.pk).exists())


class AddressRankAndBaseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("address@example.com", "password123")

    def test_only_one_default_address_per_user(self):
        values = dict(receiver_name="A User", phone_number="+14155552671", country="US", province="CA", city="SF", postal_code="94105", address="Main St")
        first = Address.objects.create(user=self.user, title="Home", is_default=True, **values)
        second = Address.objects.create(user=self.user, title="Office", is_default=True, **values)
        first.refresh_from_db()
        self.assertFalse(first.is_default)
        self.assertTrue(second.is_default)
        self.assertEqual(str(second), "Office — A User")

    def test_rank_validation_ordering_and_string(self):
        rank = Rank.objects.create(name="Gold", activation_level=2, priority=5)
        self.assertEqual(str(rank), "Gold")
        with self.assertRaises(ValidationError):
            Rank(name="X", activation_level=0).full_clean()


class AccountFormTests(TestCase):
    def test_signup_validates_passwords_and_duplicate_email(self):
        form = AccountSignUpForm(data={"email": "NEW@EXAMPLE.COM", "password1": "Strong-pass-123", "password2": "different"})
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)
        User.objects.create_user("taken@example.com", "password123")
        duplicate = AccountSignUpForm(data={"email": "TAKEN@example.com", "password1": "Strong-pass-123", "password2": "Strong-pass-123"})
        self.assertFalse(duplicate.is_valid())
        self.assertIn("email", duplicate.errors)

    def test_signup_save_and_account_forms(self):
        form = AccountSignUpForm(data={"email": "new@example.com", "password1": "Strong-pass-123", "password2": "Strong-pass-123"})
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(user.check_password("Strong-pass-123"))
        account_form = AccountForm(instance=user)
        self.assertEqual(len(account_form.fieldsets), 2)
        profile_form = ProfileForm(instance=user.profile)
        self.assertEqual(len(profile_form.fieldsets), 1)


class AccountViewAndUtilityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("viewer@example.com", "password123")

    def test_urls_resolve_and_private_views_require_login(self):
        self.assertEqual(reverse("accounts:sign-in"), "/accounts/sign-in/")
        response = self.client.get(reverse("accounts:account"))
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("accounts:account")).status_code, 200)
        self.assertEqual(self.client.get(reverse("accounts:account-detail")).status_code, 200)

    def test_profile_public_and_private_pages(self):
        response = self.client.get(reverse("accounts:profile", args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.user.profile.is_private = True
        self.user.profile.save()
        response = self.client.get(reverse("accounts:profile", args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get(reverse("accounts:profile", args=["missing"])).status_code, 404)

    def test_ip_ids_and_upload_helpers(self):
        request = RequestFactory().get("/", HTTP_X_FORWARDED_FOR="203.0.113.1, 10.0.0.1")
        self.assertEqual(get_user_ip_address(request), "203.0.113.1")
        self.assertIsNone(get_country_by_ip("not-an-ip"))
        self.assertEqual(len(generate_public_id()), 32)
        self.assertEqual(len(generate_slug()), 36)
        self.assertEqual(safe_extension("photo.png"), ".png")
        self.assertTrue(profile_image_upload_path(self.user.profile, "avatar.png").startswith("accounts/profiles/"))
        self.assertTrue(rank_image_upload_path(Rank(name="Gold", activation_level=1), "rank.jpg").startswith("accounts/ranks/"))
