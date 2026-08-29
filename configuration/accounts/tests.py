from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user_generates_username_from_email(self):
        user = User.objects.create_user(email="jane.doe@example.com", password="s3cret-pass!")
        self.assertEqual(user.username, "janedoe")
        self.assertTrue(user.check_password("s3cret-pass!"))

    def test_duplicate_username_gets_suffixed(self):
        User.objects.create_user(email="jane.doe@example.com", password="pw12345!")
        second = User.objects.create_user(email="jane.doe@other.com", password="pw12345!")
        self.assertEqual(second.username, "janedoe2")

    def test_profile_is_created_automatically(self):
        user = User.objects.create_user(email="new@example.com", password="pw12345!")
        self.assertTrue(hasattr(user, "profile"))


class ProfilePointsTests(TestCase):
    def test_add_points_updates_level(self):
        user = User.objects.create_user(email="points@example.com", password="pw12345!")
        user.profile.add_points(250)
        self.assertEqual(user.profile.points, 250)
        self.assertEqual(user.profile.level, 2)
