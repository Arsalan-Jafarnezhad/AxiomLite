# weblog/tests/test_permissions.py

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIRequestFactory

from weblog.permissions import (
    is_article_owner,
    require_article_owner,
    is_comment_owner,
    require_comment_owner,
)

from weblog.tests.factories import (
    UserFactory,
    ArticleFactory,
    CommentFactory,
)

User = get_user_model()


class ArticlePermissionTests(TestCase):

    def setUp(self):

        self.owner = UserFactory()

        self.other_user = UserFactory()

        self.staff_user = UserFactory(
            is_staff=True,
        )

        self.article = ArticleFactory(
            author=self.owner,
        )

    def test_article_owner_permission_true(self):

        result = is_article_owner(
            self.owner,
            self.article,
        )

        self.assertTrue(
            result,
        )

    def test_article_owner_permission_false(self):

        result = is_article_owner(
            self.other_user,
            self.article,
        )

        self.assertFalse(
            result,
        )

    def test_staff_can_manage_article(self):

        result = is_article_owner(
            self.staff_user,
            self.article,
        )

        self.assertTrue(
            result,
        )

    def test_require_article_owner_allows_owner(self):

        result = require_article_owner(
            self.owner,
            self.article,
        )

        self.assertTrue(
            result,
        )

    def test_require_article_owner_blocks_other_user(self):

        with self.assertRaises(
            PermissionError,
        ):

            require_article_owner(
                self.other_user,
                self.article,
            )


class CommentPermissionTests(TestCase):

    def setUp(self):

        self.owner = UserFactory()

        self.other_user = UserFactory()

        self.staff_user = UserFactory(
            is_staff=True,
        )

        self.comment = CommentFactory(
            author=self.owner,
        )

    def test_comment_owner_permission_true(self):

        result = is_comment_owner(
            self.owner,
            self.comment,
        )

        self.assertTrue(
            result,
        )

    def test_comment_owner_permission_false(self):

        result = is_comment_owner(
            self.other_user,
            self.comment,
        )

        self.assertFalse(
            result,
        )

    def test_staff_can_manage_comment(self):

        result = is_comment_owner(
            self.staff_user,
            self.comment,
        )

        self.assertTrue(
            result,
        )

    def test_require_comment_owner_allows_owner(self):

        result = require_comment_owner(
            self.owner,
            self.comment,
        )

        self.assertTrue(
            result,
        )

    def test_require_comment_owner_blocks_other_user(self):

        with self.assertRaises(
            PermissionError,
        ):

            require_comment_owner(
                self.other_user,
                self.comment,
            )


class AuthenticationPermissionTests(TestCase):

    def test_anonymous_user_cannot_own_article(self):

        from django.contrib.auth.models import AnonymousUser

        anonymous = AnonymousUser()

        article = ArticleFactory()

        self.assertFalse(
            is_article_owner(
                anonymous,
                article,
            )
        )

    def test_anonymous_user_cannot_own_comment(self):

        from django.contrib.auth.models import AnonymousUser

        anonymous = AnonymousUser()

        comment = CommentFactory()

        self.assertFalse(
            is_comment_owner(
                anonymous,
                comment,
            )
        )


class PermissionEdgeCaseTests(TestCase):

    def test_deleted_user_article_permission(self):

        user = UserFactory()

        article = ArticleFactory(
            author=user,
        )

        user.delete()

        self.assertFalse(
            is_article_owner(
                user,
                article,
            )
        )

    def test_none_user_permission(self):

        article = ArticleFactory()

        self.assertFalse(
            is_article_owner(
                None,
                article,
            )
        )

    def test_none_object_permission(self):

        user = UserFactory()

        self.assertFalse(
            is_article_owner(
                user,
                None,
            )
        )
