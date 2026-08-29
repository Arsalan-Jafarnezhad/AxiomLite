# weblog/tests/test_models.py

from django.test import TestCase
from django.utils import timezone

from weblog.models import (
    Article,
    Category,
    Tag,
    Series,
    Comment,
    ArticleView,
    ArticleSEO,
    Media,
)

from weblog.tests.factories import (
    UserFactory,
    ArticleFactory,
    CategoryFactory,
    TagFactory,
    SeriesFactory,
    CommentFactory,
    ArticleViewFactory,
    ArticleSEOFactory,
    MediaFactory,
)


class CategoryModelTest(TestCase):

    def test_create_category(self):

        category = CategoryFactory()

        self.assertEqual(
            str(category),
            category.name,
        )

        self.assertTrue(
            category.slug,
        )


class TagModelTest(TestCase):

    def test_create_tag(self):

        tag = TagFactory()

        self.assertEqual(
            str(tag),
            tag.name,
        )

        self.assertTrue(
            tag.slug,
        )


class SeriesModelTest(TestCase):

    def test_create_series(self):

        series = SeriesFactory()

        self.assertEqual(
            str(series),
            series.title,
        )


class ArticleModelTest(TestCase):

    def setUp(self):

        self.user = UserFactory()

        self.article = ArticleFactory(
            author=self.user,
        )

    def test_article_creation(self):

        self.assertEqual(
            self.article.author,
            self.user,
        )

        self.assertEqual(
            self.article.status,
            Article.Status.PUBLISHED,
        )

    def test_article_string(self):

        self.assertEqual(
            str(self.article),
            self.article.title,
        )

    def test_article_absolute_url(self):

        url = self.article.get_absolute_url()

        self.assertIn(
            self.article.slug,
            url,
        )

    def test_article_is_published(self):

        self.article.status = Article.Status.PUBLISHED

        self.article.published_at = timezone.now()

        self.article.save()

        self.assertTrue(
            self.article.is_published,
        )

    def test_article_reading_minutes(self):

        self.assertGreater(
            self.article.reading_minutes,
            0,
        )

    def test_article_reading_time(self):

        self.assertGreaterEqual(
            self.article.reading_time,
            1,
        )

    def test_article_tags(self):

        tag = TagFactory()

        self.article.tags.add(
            tag,
        )

        self.assertIn(
            tag,
            self.article.tags.all(),
        )

    def test_article_category_relation(self):

        category = CategoryFactory()

        self.article.category = category

        self.article.save()

        self.assertEqual(
            self.article.category,
            category,
        )


class CommentModelTest(TestCase):

    def test_comment_creation(self):

        comment = CommentFactory()

        self.assertEqual(
            comment.article.__class__,
            Article,
        )

        self.assertEqual(
            str(comment),
            comment.body,
        )

    def test_comment_status(self):

        comment = CommentFactory()

        self.assertEqual(
            comment.status,
            Comment.Status.APPROVED,
        )


class ArticleViewModelTest(TestCase):

    def test_article_view_creation(self):

        view = ArticleViewFactory()

        self.assertEqual(
            view.article.__class__,
            Article,
        )

        self.assertEqual(
            view.ip_address,
            "127.0.0.1",
        )


class SEOModelTest(TestCase):

    def test_seo_creation(self):

        seo = ArticleSEOFactory()

        self.assertEqual(
            seo.article.__class__,
            Article,
        )

        self.assertTrue(
            seo.meta_title,
        )


class MediaModelTest(TestCase):

    def test_media_creation(self):

        media = MediaFactory()

        self.assertEqual(
            media.article.__class__,
            Article,
        )

        self.assertTrue(
            media.file,
        )


class ArticleManagerTest(TestCase):

    def setUp(self):

        self.published = ArticleFactory(
            status=Article.Status.PUBLISHED,
        )

        self.draft = ArticleFactory(
            status=Article.Status.DRAFT,
        )

        self.review = ArticleFactory(
            status=Article.Status.REVIEW,
        )

    def test_published_queryset(self):

        queryset = Article.objects.published()

        self.assertIn(
            self.published,
            queryset,
        )

        self.assertNotIn(
            self.draft,
            queryset,
        )

    def test_drafts_queryset(self):

        queryset = Article.objects.drafts()

        self.assertIn(
            self.draft,
            queryset,
        )

    def test_review_queryset(self):

        queryset = Article.objects.review()

        self.assertIn(
            self.review,
            queryset,
        )
