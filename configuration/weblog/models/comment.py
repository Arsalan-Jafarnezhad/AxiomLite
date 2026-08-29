from django.conf import settings
from django.db import models
from django.utils import timezone

from weblog.managers.comment import CommentManager
from weblog.utils.sentiment import analyze


class Comment(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    class Sentiment(models.TextChoices):
        POSITIVE = "positive", "Positive"
        NEUTRAL = "neutral", "Neutral"
        NEGATIVE = "negative", "Negative"

    article = models.ForeignKey(
        "weblog.Article",
        on_delete=models.CASCADE,
        related_name="comments",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
    )

    body = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    sentiment_score = models.FloatField(
        default=0.0,
        db_index=True,
    )

    sentiment_label = models.CharField(
        max_length=20,
        choices=Sentiment.choices,
        default=Sentiment.NEUTRAL,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    objects = CommentManager()

    def analyze_sentiment(self):
        return analyze(self.body or "")

    def refresh_sentiment(self):
        score, label = self.analyze_sentiment()

        self.sentiment_score = score
        self.sentiment_label = label

        return self

    @property
    def sentiment_percentage(self):
        return round(
            (self.sentiment_score + 1) * 50,
            1,
        )

    @property
    def sentiment_icon(self):
        return {
            self.Sentiment.POSITIVE: "sentiment_satisfied",
            self.Sentiment.NEUTRAL: "sentiment_neutral",
            self.Sentiment.NEGATIVE: "sentiment_dissatisfied",
        }.get(
            self.sentiment_label,
            "sentiment_neutral",
        )

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def soft_delete(self):
        """
        Soft-delete this comment.

        The database row remains intact.
        """
        self.deleted_at = timezone.now()

        self.save(
            update_fields=[
                "deleted_at",
                "updated_at",
            ]
        )

        return self

    def restore(self):
        """
        Restore a soft-deleted comment.
        """
        self.deleted_at = None

        self.save(
            update_fields=[
                "deleted_at",
                "updated_at",
            ]
        )

        return self

    def save(self, *args, **kwargs):
        """
        Recalculate sentiment whenever the comment body is saved.

        If update_fields is supplied without sentiment fields, don't
        unnecessarily recalculate sentiment-related database fields.
        """

        update_fields = kwargs.get("update_fields")

        if update_fields is None:
            self.refresh_sentiment()

        elif "body" in update_fields:
            self.refresh_sentiment()

            update_fields = set(update_fields)
            update_fields.update(
                {
                    "sentiment_score",
                    "sentiment_label",
                }
            )

            kwargs["update_fields"] = update_fields

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Override Django's default hard delete.

        Calling comment.delete() now performs a soft delete.
        """

        return self.soft_delete()

    def __str__(self):
        return f"{self.author} — {self.article}"

