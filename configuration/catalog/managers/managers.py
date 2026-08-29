"""
shop/managers.py

Custom Manager and QuerySet classes.

django-model-utils' ``SoftDeletableManager`` is used as the base for soft-
delete support instead of a hand-rolled one.  See:
https://django-model-utils.readthedocs.io/en/latest/managers.html
"""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.db.models.query_utils import Q
from django.utils.timezone import now as timezone_now

# django-model-utils — pip install django-model-utils
from model_utils.managers import SoftDeletableManager


# ── OffCode ───────────────────────────────────────────────────────────────────

class OffCodeQuerySet(models.QuerySet):
    """Chainable queryset helpers for OffCode filtering."""

    def active(self) -> "OffCodeQuerySet":
        """
        Codes that are:
        - flagged ``is_active``
        - within their validity window
        - have at least one discount type set
        """
        now = timezone_now()
        return self.filter(
            Q(ends_at__gte=now) | Q(ends_at__isnull=True),
            starts_at__lte=now,
            is_active=True,
        ).exclude(
            Q(discount_percent__isnull=True) & Q(fixed_discount_amount__isnull=True)
        )

    def applicable_for(self, order_total: Decimal) -> "OffCodeQuerySet":
        """
        Chains ``.active()`` and filters to codes whose minimum order amount
        (if any) is not exceeded.  Per-user checks still happen at application
        time inside the model.
        """
        return self.active().filter(
            Q(minimum_order_amount__isnull=True)
            | Q(minimum_order_amount__lte=order_total)
        )


class OffCodeManager(SoftDeletableManager):
    """Manager for ``OffCode`` with two best-code finders."""

    def get_queryset(self) -> OffCodeQuerySet:
        return OffCodeQuerySet(self.model, using=self._db).filter(
            is_removed=False  # SoftDeletableModel uses `is_removed`
        )

    def active(self) -> OffCodeQuerySet:
        return self.get_queryset().active()

    # ── Finders ──────────────────────────────────────────────────────────────

    def best_for_lowest_price(self, order_total: Decimal):
        """Code that yields the lowest final price for ``order_total``."""
        best, lowest = None, Decimal("Infinity")
        for code in self.get_queryset().applicable_for(order_total):
            if not code.is_valid_for_general_check:
                continue
            discount = code.calculate_discount_amount(order_total)
            final = order_total - discount
            if final < lowest:
                lowest, best = final, code
        return best

    def best_for_highest_discount(self, order_total: Decimal):
        """Code that yields the greatest raw discount for ``order_total``."""
        best, maximum = None, Decimal("-Infinity")
        for code in self.get_queryset().applicable_for(order_total):
            if not code.is_valid:
                continue
            discount = code.calculate_discount_amount(order_total)
            if discount > maximum:
                maximum, best = discount, code
        return best
