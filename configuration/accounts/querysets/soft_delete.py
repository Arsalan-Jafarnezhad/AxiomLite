from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet providing soft-delete operations."""

    def delete(self):
        """Soft-delete all objects in the queryset."""
        return super().update(
            is_deleted=True,
            deleted_at=timezone.now(),
        )

    def hard_delete(self):
        """Permanently delete all objects in the queryset."""
        return super().delete()

    def alive(self):
        """Return objects that have not been soft-deleted."""
        return self.filter(is_deleted=False)

    def deleted(self):
        """Return only soft-deleted objects."""
        return self.filter(is_deleted=True)
