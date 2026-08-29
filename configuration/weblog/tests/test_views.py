# weblog/tests/test_views.py

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from weblog.models import (
    Article,
    Comment,
)

from weblog.tests.factories import (
    UserFactory,
    ArticleFactory,
    CategoryFactory,
    TagFactory,
    SeriesFactory,
    CommentFactory,
)


User = get_user_model()



class PublicArticleViewTests(TestCase):

    def setUp(self):

        self.article = ArticleFactory(
            status=Article.Status.PUBLISHED,
        )


    def test_article_detail_page_status_code(self):

        response = self.client.get(
            self.article.get_absolute_url()
        )

        self.assertEqual(
            response.status_code,
            200,
        )


    def test_article_detail_contains_title(self):

        response = self.client.get(
            self.article.get_absolute_url()
        )

        self.assertContains(
            response,
            self.article.title,
        )


    def test_article_list_view(self):

        ArticleFactory()

        response = self.client.get(
            reverse(
                "weblog:article-list"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )


    def test_category_page(self):

        category = CategoryFactory()

        article = ArticleFactory(
            category=category,
        )

        response = self.client.get(
            reverse(
                "weblog:category",
                kwargs={
                    "slug": category.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            article.title,
        )


    def test_tag_page(self):

        tag = TagFactory()

        article = ArticleFactory()

        article.tags.add(
            tag,
        )

        response = self.client.get(
            reverse(
                "weblog:tag",
                kwargs={
                    "slug": tag.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            article.title,
        )


    def test_series_page(self):

        series = SeriesFactory()

        article = ArticleFactory(
            series=series,
        )

        response = self.client.get(
            reverse(
                "weblog:series",
                kwargs={
                    "slug": series.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            article.title,
        )


    def test_author_page(self):

        user = UserFactory()

        article = ArticleFactory(
            author=user,
        )

        response = self.client.get(
            reverse(
                "weblog:author",
                kwargs={
                    "username": user.username,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            article.title,
        )



class SearchViewTests(TestCase):

    def test_search_article(self):

        article = ArticleFactory(
            title="Django Testing Article",
        )

        response = self.client.get(
            reverse(
                "weblog:search",
            ),
            {
                "q": "Django",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            article.title,
        )



class CommentViewTests(TestCase):

    def setUp(self):

        self.user = UserFactory()

        self.article = ArticleFactory()

        self.client.login(
            username=self.user.username,
            password="password123",
        )


    def test_create_comment_requires_login(self):

        self.client.logout()

        response = self.client.post(
            reverse(
                "weblog:comment-create",
            ),
            {
                "article": self.article.pk,
                "body": "Test comment",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )


    def test_comment_creation(self):

        response = self.client.post(
            reverse(
                "weblog:comment-create",
            ),
            {
                "article": self.article.pk,
                "body": "New comment",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            Comment.objects.filter(
                body="New comment",
            ).exists()
        )



class DashboardViewTests(TestCase):

    def setUp(self):

        self.user = UserFactory()

        self.client.login(
            username=self.user.username,
            password="password123",
        )


    def test_dashboard_requires_authentication(self):

        self.client.logout()

        response = self.client.get(
            reverse(
                "weblog:dashboard",
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )


    def test_dashboard_access(self):

        response = self.client.get(
            reverse(
                "weblog:dashboard",
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )


    def test_user_articles_only_visible(self):

        own_article = ArticleFactory(
            author=self.user,
        )

        other_article = ArticleFactory()

        response = self.client.get(
            reverse(
                "weblog:dashboard:articles",
            )
        )

        self.assertContains(
            response,
            own_article.title,
        )

        self.assertNotContains(
            response,
            other_article.title,
        )



class ArchiveViewTests(TestCase):

    def test_archive_page(self):

        ArticleFactory()

        response = self.client.get(
            reverse(
                "weblog:archive",
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )