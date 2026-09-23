"""Tests for the accounts API."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Address, Profile, User


class AccountsAPITestCase(APITestCase):
    """Base test case for accounts API tests."""

    @classmethod
    def setUpTestData(cls):
        """Create shared test data."""
        cls.user = User.objects.create_user(
            username="arsalan",
            email="arsalan@example.com",
            password="StrongPassword123!",
            first_name="Arsalan",
            last_name="Jafarnezhad",
        )

        cls.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPassword123!",
            first_name="Other",
            last_name="User",
        )

    def setUp(self):
        """Authenticate as the primary test user."""
        self.client.force_authenticate(user=self.user)


class AuthenticationAPITests(AccountsAPITestCase):
    """Test API authentication requirements."""

    def test_account_requires_authentication(self):
        """Account endpoint requires authentication."""
        self.client.force_authenticate(user=None)

        response = self.client.get(
            reverse("accounts:api:me"),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_profile_requires_authentication(self):
        """Own profile endpoint requires authentication."""
        self.client.force_authenticate(user=None)

        response = self.client.get(
            reverse("accounts:api:profile"),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_addresses_require_authentication(self):
        """Address endpoint requires authentication."""
        self.client.force_authenticate(user=None)

        response = self.client.get(
            reverse("accounts:api:address-list"),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_public_profile_does_not_require_authentication(self):
        """Public profiles can be viewed anonymously."""
        self.client.force_authenticate(user=None)

        response = self.client.get(
            reverse(
                "accounts:api:public-profile",
                kwargs={"username": self.user.username},
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )


class AccountAPITests(AccountsAPITestCase):
    """Test account endpoints."""

    def test_get_current_account(self):
        """Authenticated users can retrieve their account."""
        response = self.client.get(
            reverse("accounts:api:me"),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["username"],
            "arsalan",
        )
        self.assertEqual(
            response.data["email"],
            "arsalan@example.com",
        )

    def test_update_current_account(self):
        """Authenticated users can update their account."""
        response = self.client.patch(
            reverse("accounts:api:me"),
            {
                "first_name": "Arsalan Updated",
                "preferred_language": "en",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.first_name,
            "Arsalan Updated",
        )
        self.assertEqual(
            self.user.preferred_language,
            "en",
        )

    def test_email_cannot_be_changed(self):
        """Email is read-only through the account API."""
        response = self.client.patch(
            reverse("accounts:api:me"),
            {
                "email": "new@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.email,
            "arsalan@example.com",
        )


class ProfileAPITests(AccountsAPITestCase):
    """Test profile endpoints."""

    def test_get_own_profile(self):
        """Authenticated users can retrieve their profile."""
        response = self.client.get(
            reverse("accounts:api:profile"),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["public_id"],
            str(self.user.profile.public_id),
        )

    def test_update_own_profile(self):
        """Authenticated users can update their profile."""
        response = self.client.patch(
            reverse("accounts:api:profile"),
            {
                "display_name": "Arsalan",
                "biography": "Backend developer.",
                "is_private": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        profile = Profile.objects.get(
            user=self.user,
        )

        self.assertEqual(
            profile.display_name,
            "Arsalan",
        )
        self.assertEqual(
            profile.biography,
            "Backend developer.",
        )
        self.assertFalse(profile.is_private)

    def test_public_profile(self):
        """Public profiles expose public information."""
        self.user.profile.is_private = False
        self.user.profile.biography = "Public biography."
        self.user.profile.save()

        response = self.client.get(
            reverse(
                "accounts:api:public-profile",
                kwargs={"username": self.user.username},
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["username"],
            self.user.username,
        )
        self.assertEqual(
            response.data["biography"],
            "Public biography.",
        )

    def test_private_profile_hides_private_information(self):
        """Private profiles hide sensitive information."""
        self.user.profile.is_private = True
        self.user.profile.biography = "Private biography."
        self.user.profile.points = 100
        self.user.profile.level = 5
        self.user.profile.save()

        self.client.force_authenticate(
            user=self.other_user,
        )

        response = self.client.get(
            reverse(
                "accounts:api:public-profile",
                kwargs={"username": self.user.username},
            ),
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertNotIn(
            "biography",
            response.data,
        )
        self.assertNotIn(
            "points",
            response.data,
        )
        self.assertNotIn(
            "level",
            response.data,
        )

    def test_owner_can_view_private_profile(self):
        """Profile owners can see their complete public representation."""
        self.user.profile.is_private = True
        self.user.profile.biography = "Private biography."
        self.user.profile.points = 100
        self.user.profile.level = 5
        self.user.profile.save()

        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            reverse(
                "accounts:api:profile",
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["biography"],
            "Private biography.",
        )
        self.assertEqual(
            response.data["points"],
            100,
        )
        self.assertEqual(
            response.data["level"],
            5,
        )


class AddressAPITests(AccountsAPITestCase):
    """Test address endpoints."""

    def test_list_addresses_only_returns_own_addresses(self):
        """Users can only list their own addresses."""
        Address.objects.create(
            user=self.user,
            title="Home",
            receiver_name="Arsalan",
            phone_number="+989121234567",
            country="IR",
            province="West Azerbaijan",
            city="Urmia",
            postal_code="1234567890",
            address="Test address",
        )

        Address.objects.create(
            user=self.other_user,
            title="Other",
            receiver_name="Other",
            phone_number="+989121111111",
            country="IR",
            province="Tehran",
            city="Tehran",
            postal_code="0987654321",
            address="Other address",
        )

        response = self.client.get(
            reverse("accounts:api:address-list"),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        if isinstance(response.data, dict):
            addresses = response.data["results"]
        else:
            addresses = response.data

        self.assertEqual(
            len(addresses),
            1,
        )

    def test_create_address(self):
        """Users can create an address for themselves."""
        response = self.client.post(
            reverse("accounts:api:address-list"),
            {
                "title": "Home",
                "receiver_name": "Arsalan",
                "phone_number": "+989121234567",
                "country": "IR",
                "province": "West Azerbaijan",
                "city": "Urmia",
                "postal_code": "1234567890",
                "address": "Test address",
                "is_default": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        address = Address.objects.get(
            public_id=response.data["public_id"],
        )

        self.assertEqual(
            address.user,
            self.user,
        )
        self.assertTrue(
            address.is_default,
        )

    def test_user_cannot_access_other_users_address(self):
        """Users cannot access another user's address."""
        address = Address.objects.create(
            user=self.other_user,
            title="Other",
            receiver_name="Other",
            phone_number="+989121111111",
            country="IR",
            province="Tehran",
            city="Tehran",
            postal_code="0987654321",
            address="Other address",
        )

        response = self.client.get(
            reverse(
                "accounts:api:address-detail",
                kwargs={"public_id": address.public_id},
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_user_cannot_delete_other_users_address(self):
        """Users cannot delete another user's address."""
        address = Address.objects.create(
            user=self.other_user,
            title="Other",
            receiver_name="Other",
            phone_number="+989121111111",
            country="IR",
            province="Tehran",
            city="Tehran",
            postal_code="0987654321",
            address="Other address",
        )

        response = self.client.delete(
            reverse(
                "accounts:api:address-detail",
                kwargs={"public_id": address.public_id},
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            Address.objects.filter(
                pk=address.pk,
            ).exists(),
        )
