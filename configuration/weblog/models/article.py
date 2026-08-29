# weblog/models/article.py

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from accounts.models.soft_delete import SoftDeleteModel
from weblog.managers.article import ArticleManager
from weblog.utils.article.analyzer import ArticleAnalyzer
from weblog.utils.reading_time import reading_time
from weblog.utils.upload_paths import article_cover_path
from weblog.utils.slug import unique_slug


class Article(SoftDeleteModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        REVIEW = "review", "In Review"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"
        UNLISTED = "unlisted", "Unlisted"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles",
    )

    category = models.ForeignKey(
        "weblog.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )

    series = models.ForeignKey(
        "weblog.Series",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )

    tags = models.ManyToManyField(
        "weblog.Tag",
        blank=True,
        related_name="articles",
    )

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    summary = models.TextField(blank=True)
    content = models.TextField()

    cover = models.ImageField(
        upload_to=article_cover_path,
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
        db_index=True,
    )

    allow_comments = models.BooleanField(default=True)

    is_featured = models.BooleanField(default=False, db_index=True)
    is_pinned = models.BooleanField(default=False, db_index=True)

    reading_minutes = models.PositiveSmallIntegerField(
        default=1,
        editable=False,
        db_index=True,
    )

    score = models.PositiveSmallIntegerField(
        default=0,
        editable=False,
        db_index=True,
    )

    published_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
    )

    scheduled_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    ai_score = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        editable=False,
    )

    ai_analysis = models.JSONField(
        null=True,
        blank=True,
        editable=False,
    )

    ai_analyzed_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
    )

    objects = ArticleManager()

    class Meta:
        ordering = ("-published_at", "-created_at")
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["visibility"]),
            models.Index(fields=["published_at"]),
            models.Index(fields=["author"]),
            models.Index(fields=["category"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["is_featured"]),
            models.Index(fields=["is_pinned"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        old_score = 0
        old_is_published = False
        old_content = None

        if self.pk:
            old_article = (
                Article.objects.filter(pk=self.pk)
                .values(
                    "content",
                    "score",
                    "status",
                    "published_at",
                )
                .first()
            )

            if old_article:
                old_content = old_article["content"]
                old_score = old_article["score"]

                old_is_published = (
                    old_article["status"] == self.Status.PUBLISHED
                    and old_article["published_at"] is not None
                )

        content_changed = old_content != self.content

        if not self.slug:
            self.slug = unique_slug(
                Article,
                self.title,
                exclude_pk=self.pk,
            )

        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()

        self.reading_minutes = reading_time(self.content)

        analyzer = ArticleAnalyzer()

        self.score, self.ai_score, ai_result = analyzer.analyze(self.content)
        if ai_result is not None:
            self.ai_score = ai_result["score"]
            self.ai_analysis = ai_result
            self.ai_analyzed_at = timezone.now()

        elif content_changed:
            self.ai_score = None
            self.ai_analysis = None
            self.ai_analyzed_at = None

        new_is_published = (
            self.status == self.Status.PUBLISHED and self.published_at is not None
        )

        super().save(*args, **kwargs)

        old_points = old_score if old_is_published else 0
        new_points = self.score if new_is_published else 0

        points_delta = new_points - old_points

        if points_delta:
            self.author.profile.add_points(points_delta)

    def get_absolute_url(self):
        return reverse(
            "weblog:article-detail",
            kwargs={"slug": self.slug},
        )

    @property
    def is_published(self):
        return (
            self.status == self.Status.PUBLISHED
            and self.published_at
            and self.published_at <= timezone.now()
        )

    @property
    def reading_time(self):
        return self.reading_minutes

    @property
    def comments_count(self):
        return self.comments.filter(status="approved").count()

    @property
    def views_count(self):
        return self.views.count()

    @property
    def bookmarks_count(self):
        return self.bookmarks.count()

    @property
    def reactions_count(self):
        return self.reactions.count()

    @property
    def reading_time_display(self):
        if self.reading_minutes == 1:
            return "1 min read"

        return f"{self.reading_minutes} min read"
