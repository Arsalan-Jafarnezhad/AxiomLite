from django.db import models
from django.utils import timezone


class ArticleQuerySet(models.QuerySet):

    # ─────────────────────────────────────────────
    # Status
    # ─────────────────────────────────────────────

    def published(self):
        return self.filter(
            status=self.model.Status.PUBLISHED,
            published_at__isnull=False,
            published_at__lte=timezone.now(),
        )

    def drafts(self):
        return self.filter(
            status=self.model.Status.DRAFT,
        )

    def review(self):
        return self.filter(
            status=self.model.Status.REVIEW,
        )

    def archived(self):
        return self.filter(
            status=self.model.Status.ARCHIVED,
        )

    # ─────────────────────────────────────────────
    # Visibility
    # ─────────────────────────────────────────────

    def public(self):
        return self.filter(
            visibility=self.model.Visibility.PUBLIC,
        )

    def private(self):
        return self.filter(
            visibility=self.model.Visibility.PRIVATE,
        )

    def unlisted(self):
        return self.filter(
            visibility=self.model.Visibility.UNLISTED,
        )

    # ─────────────────────────────────────────────
    # Flags
    # ─────────────────────────────────────────────

    def featured(self):
        return self.filter(
            is_featured=True,
        )

    def pinned(self):
        return self.filter(
            is_pinned=True,
        )

    # ─────────────────────────────────────────────
    # Publishing
    # ─────────────────────────────────────────────

    def scheduled(self):
        return self.filter(
            scheduled_at__isnull=False,
            scheduled_at__gt=timezone.now(),
        )

    def published_before(self, date):
        return self.filter(
            status=self.model.Status.PUBLISHED,
            published_at__isnull=False,
            published_at__lt=date,
        )

    def published_after(self, date):
        return self.filter(
            status=self.model.Status.PUBLISHED,
            published_at__isnull=False,
            published_at__gt=date,
        )

    def recently_published(self, days=7):
        since = timezone.now() - timezone.timedelta(days=days)

        return self.published().filter(
            published_at__gte=since,
        )

    # ─────────────────────────────────────────────
    # Relationships
    # ─────────────────────────────────────────────

    def by_author(self, author):
        return self.filter(
            author=author,
        )

    def by_category(self, category):
        return self.filter(
            category=category,
        )

    def by_series(self, series):
        return self.filter(
            series=series,
        )

    def by_tag(self, tag):
        return self.filter(
            tags=tag,
        )

    # ─────────────────────────────────────────────
    # Search
    # ─────────────────────────────────────────────

    def search(self, query):
        return self.filter(
            models.Q(title__icontains=query)
            | models.Q(subtitle__icontains=query)
            | models.Q(summary__icontains=query)
            | models.Q(content__icontains=query)
        )

    def title_search(self, query):
        return self.filter(
            title__icontains=query,
        )

    # ─────────────────────────────────────────────
    # Reading time
    # ─────────────────────────────────────────────

    def quick_reads(self, maximum=3):
        return self.filter(
            reading_minutes__lte=maximum,
        )

    def long_reads(self, minimum=10):
        return self.filter(
            reading_minutes__gte=minimum,
        )

    def reading_time_between(
        self,
        minimum,
        maximum,
    ):
        return self.filter(
            reading_minutes__range=(
                minimum,
                maximum,
            ),
        )

    # ─────────────────────────────────────────────
    # Common combinations
    # ─────────────────────────────────────────────

    def public_published(self):
        return self.published().public()

    def featured_published(self):
        return self.published().featured()

    def pinned_published(self):
        return self.published().pinned()

    def featured_public(self):
        return self.public().featured()

    def pinned_public(self):
        return self.public().pinned()

    def discoverable(self):
        return self.published().filter(
            visibility=self.model.Visibility.PUBLIC,
        )

    # ─────────────────────────────────────────────
    # Ordering
    # ─────────────────────────────────────────────

    def newest(self):
        return self.order_by(
            "-published_at",
            "-created_at",
        )

    def oldest(self):
        return self.order_by(
            "published_at",
            "created_at",
        )

    def most_recent(self):
        return self.order_by(
            "-created_at",
        )

    def most_read(self):
        return self.order_by(
            "-views_count",
        )

    # ─────────────────────────────────────────────
    # Utility
    # ─────────────────────────────────────────────

    def with_author(self):
        return self.select_related(
            "author",
        )

    def with_category(self):
        return self.select_related(
            "category",
        )

    def with_series(self):
        return self.select_related(
            "series",
        )

    def with_relations(self):
        return self.select_related(
            "author",
            "category",
            "series",
        ).prefetch_related(
            "tags",
        )


class ArticleManager(models.Manager.from_queryset(ArticleQuerySet)):
    pass
