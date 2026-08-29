from django.db import models


class CommentQuerySet(models.QuerySet):

    # ============================================================
    # Soft deletion
    # ============================================================

    def not_deleted(self):
        return self.filter(
            deleted_at__isnull=True,
        )

    def deleted(self):
        return self.filter(
            deleted_at__isnull=False,
        )

    def soft_delete(self):
        from django.utils import timezone

        return self.update(
            deleted_at=timezone.now(),
            updated_at=timezone.now(),
        )

    def restore(self):
        from django.utils import timezone

        return self.update(
            deleted_at=None,
            updated_at=timezone.now(),
        )

    # ============================================================
    # Status
    # ============================================================

    def approved(self):
        return self.not_deleted().filter(
            status=self.model.Status.APPROVED,
        )

    def pending(self):
        return self.not_deleted().filter(
            status=self.model.Status.PENDING,
        )

    def rejected(self):
        return self.not_deleted().filter(
            status=self.model.Status.REJECTED,
        )

    def moderated(self):
        return self.not_deleted().exclude(
            status=self.model.Status.PENDING,
        )

    # ============================================================
    # Structure
    # ============================================================

    def root_comments(self):
        return self.filter(
            parent__isnull=True,
        )

    def replies(self):
        return self.filter(
            parent__isnull=False,
        )

    def for_parent(self, parent):
        return self.filter(
            parent=parent,
        )

    # ============================================================
    # Relationships
    # ============================================================

    def for_article(self, article):
        return self.filter(
            article=article,
        )

    def by_user(self, user):
        return self.filter(
            author=user,
        )

    def by_author(self, author):
        return self.filter(
            author=author,
        )

    # ============================================================
    # Visibility
    # ============================================================

    def visible(self):
        return self.not_deleted().filter(
            status=self.model.Status.APPROVED,
        )

    def visible_for_article(self, article):
        return self.for_article(article).visible()

    def root_visible(self):
        return self.visible().root_comments()

    def replies_visible(self):
        return self.visible().replies()

    # ============================================================
    # Ordering
    # ============================================================

    def recent(self):
        return self.order_by(
            "-created_at",
        )

    def oldest(self):
        return self.order_by(
            "created_at",
        )

    def recently_updated(self):
        return self.order_by(
            "-updated_at",
        )

    # ============================================================
    # Time
    # ============================================================

    def created_before(self, date):
        return self.filter(
            created_at__lt=date,
        )

    def created_after(self, date):
        return self.filter(
            created_at__gt=date,
        )

    def updated_before(self, date):
        return self.filter(
            updated_at__lt=date,
        )

    def updated_after(self, date):
        return self.filter(
            updated_at__gt=date,
        )

    # ============================================================
    # Search
    # ============================================================

    def search(self, query):
        return self.not_deleted().filter(
            models.Q(body__icontains=query)
            | models.Q(author__username__icontains=query)
        )

    # ============================================================
    # Relations
    # ============================================================

    def with_author(self):
        return self.select_related(
            "author",
        )

    def with_article(self):
        return self.select_related(
            "article",
        )

    def with_parent(self):
        return self.select_related(
            "parent",
        )

    def with_relations(self):
        return self.select_related(
            "author",
            "article",
            "parent",
        ).prefetch_related(
            "replies",
        )

    def with_replies(self):
        return self.prefetch_related(
            "replies",
        )

    def with_reply_authors(self):
        return self.prefetch_related(
            models.Prefetch(
                "replies",
                queryset=(
                    self.model.objects.not_deleted().select_related("author").recent()
                ),
            )
        )

    # ============================================================
    # Moderation
    # ============================================================

    def needing_moderation(self):
        return self.not_deleted().filter(
            status=self.model.Status.PENDING,
        )

    def approved_replies(self):
        return self.replies().approved()

    def approved_roots(self):
        return self.root_comments().approved()

    # ============================================================
    # Sentiment
    # ============================================================

    def positive(self):
        return self.not_deleted().filter(
            sentiment_label=self.model.Sentiment.POSITIVE,
        )

    def negative(self):
        return self.not_deleted().filter(
            sentiment_label=self.model.Sentiment.NEGATIVE,
        )

    def neutral(self):
        return self.not_deleted().filter(
            sentiment_label=self.model.Sentiment.NEUTRAL,
        )


class CommentManager(models.Manager.from_queryset(CommentQuerySet)):
    pass
