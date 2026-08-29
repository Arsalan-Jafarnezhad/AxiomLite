# weblog/tests/test_api.py

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from weblog.models import Article

from weblog.tests.factories import (
    UserFactory,
    ArticleFactory,
    CategoryFactory,
    TagFactory,
    CommentFactory,
)


class ArticleAPITestCase(APITestCase):

    def setUp(self):

        self.user = UserFactory()

        self.article = ArticleFactory(
            author=self.user,
        )

        self.client.force_authenticate(
            user=self.user,
        )

    def test_article_list_api(self):

        response = self.client.get(
            reverse(
                "weblog-api:article-list",
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertGreaterEqual(
            len(response.data["results"]),
            1,
        )

    def test_article_detail_api(self):

        response = self.client.get(
            reverse(
                "weblog-api:article-detail",
                kwargs={
                    "slug": self.article.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["title"],
            self.article.title,
        )

    def test_create_article_api(self):

        payload = {
            "title": "API Article",
            "content": "API content",
            "summary": "API summary",
        }

        response = self.client.post(
            reverse(
                "weblog-api:article-list",
            ),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Article.objects.filter(
                title="API Article",
            ).exists()
        )

    def test_update_article_api(self):

        response = self.client.patch(
            reverse(
                "weblog-api:article-detail",
                kwargs={
                    "slug": self.article.slug,
                },
            ),
            {
                "title": "Updated title",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.article.refresh_from_db()

        self.assertEqual(
            self.article.title,
            "Updated title",
        )

    def test_delete_article_api(self):

        response = self.client.delete(
            reverse(
                "weblog-api:article-detail",
                kwargs={
                    "slug": self.article.slug,
                },
            )
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_204_NO_CONTENT,
                status.HTTP_200_OK,
            ],
        )


class ArticleFilterAPITests(APITestCase):

    def setUp(self):

        self.category = CategoryFactory()

        self.tag = TagFactory()

        self.article = ArticleFactory(
            category=self.category,
        )

        self.article.tags.add(
            self.tag,
        )

    def test_filter_by_category(self):

        response = self.client.get(
            reverse(
                "weblog-api:article-list",
            ),
            {
                "category": self.category.slug,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

    def test_search_api(self):

        response = self.client.get(
            reverse(
                "weblog-api:article-list",
            ),
            {
                "search": self.article.title,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )


class CommentAPITestCase(APITestCase):

    def setUp(self):

        self.user = UserFactory()

        self.article = ArticleFactory()

        self.comment = CommentFactory(
            article=self.article,
            author=self.user,
        )

        self.client.force_authenticate(
            user=self.user,
        )

    def test_comment_list_api(self):

        response = self.client.get(
            reverse(
                "weblog-api:comment-list",
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_create_comment_api(self):

        response = self.client.post(
            reverse(
                "weblog-api:comment-list",
            ),
            {
                "article": self.article.pk,
                "body": "API comment",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_delete_comment_api(self):

        response = self.client.delete(
            reverse(
                "weblog-api:comment-detail",
                kwargs={
                    "pk": self.comment.pk,
                },
            )
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_204_NO_CONTENT,
                status.HTTP_200_OK,
            ],
        )


class AuthenticationAPITests(APITestCase):

    def test_unauthenticated_create_article(self):

        response = self.client.post(
            reverse(
                "weblog-api:article-list",
            ),
            {
                "title": "Test",
                "content": "Content",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
