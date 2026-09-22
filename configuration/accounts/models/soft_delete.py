"""Reusable soft-delete model and queryset implementations."""

from django.db import models
from django.utils import timezone

from .base import BaseModel

from accounts.managers.soft_delete import SoftDeleteManager
from accounts.querysets.soft_delete import SoftDeleteQuerySet


class SoftDeleteModel(BaseModel):
    """Abstract model supporting soft deletion and restoration."""

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(
        self,
        using=None,
        keep_parents=False,
    ):
        """Soft-delete this instance."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(
            using=using,
            update_fields=[
                "is_deleted",
                "deleted_at",
            ],
        )

    def restore(self):
        """Restore a previously soft-deleted instance."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(
            update_fields=[
                "is_deleted",
                "deleted_at",
            ],
        )
