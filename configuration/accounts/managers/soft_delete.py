from django.db import models
from django.utils import timezone

from accounts.querysets.soft_delete import SoftDeleteQuerySet


class SoftDeleteManager(models.Manager):
    """Default manager that hides soft-deleted objects."""

    def get_queryset(self):
        """Return only alive objects."""
        return SoftDeleteQuerySet(
            self.model,
            using=self._db,
        ).alive()
