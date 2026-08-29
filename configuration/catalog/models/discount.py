"""
catalog/models/discount.py

OffCode — promotional discount / coupon model.

Third-party deps used
─────────────────────
- django-money (MoneyField)   pip install django-money
- django-model-utils          pip install django-model-utils
- django-lifecycle            pip install django-lifecycle

``MoneyField`` stores both the amount (``DecimalField``) and the currency
(``CharField``) in two DB columns, e.g.:

    fixed_discount_amount          → Decimal
    fixed_discount_amount_currency → CharField (ISO 4217 code)

When you read ``instance.fixed_discount_amount`` you get a ``Money`` object
with ``.amount`` and ``.currency`` attributes.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinLengthValidator, MinValueValidator
from django.db import models
from django.db.models.query_utils import Q
from django.utils.timezone import now as timezone_now
from django.utils.translation import gettext_lazy as _

# django-model-utils: SoftDeletableModel adds `is_removed` + soft-delete manager
from model_utils.models import SoftDeletableModel, TimeStampedModel

# django-lifecycle: declarative lifecycle hooks (@hook) replacing save() overrides
from django_lifecycle import LifecycleModel, hook, BEFORE_UPDATE, AFTER_CREATE

# django-money
from djmoney.models.fields import MoneyField
from moneyed import Money

from catalog.managers.managers import OffCodeManager


class OffCode(LifecycleModel, SoftDeletableModel, TimeStampedModel):
    """
    Promotional discount code.

    Supports:
    - Percentage OR fixed-amount discount (mutually exclusive)
    - Optional time window (``starts_at`` / ``ends_at``)
    - Global usage cap (``usage_limit``) and per-user cap
    - Total monetary budget cap (``total_discount_capacity``)
    - Minimum order amount gate (``minimum_order_amount``)
    - Multi-currency fixed discounts via ``MoneyField``
    """

    code = models.CharField(
        max_length=32,
        unique=True,
        validators=[MinLengthValidator(1)],
        help_text=_("Unique alphanumeric code for the discount."),
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Optional human-readable description of the offer."),
    )

    # ── Validity window ───────────────────────────────────────────────────────
    starts_at = models.DateTimeField(
        default=timezone_now,
        blank=True,
        help_text=_("When the code becomes active."),
    )
    ends_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Expiry datetime. Blank = never expires."),
    )

    # ── Discount type (percentage XOR fixed amount) ───────────────────────────
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
        help_text=_("Percentage off (0–100). Mutually exclusive with fixed_discount_amount."),
    )

    # MoneyField automatically creates two DB columns:
    #   fixed_discount_amount          → Decimal
    #   fixed_discount_amount_currency → CharField (3-char ISO code)
    fixed_discount_amount = MoneyField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        default_currency=None,  # Must be set explicitly per code
        help_text=_("Fixed monetary discount. Mutually exclusive with discount_percent."),
    )

    # ── Per-use / budget caps ─────────────────────────────────────────────────
    max_discount_per_use = MoneyField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        default_currency=None,
        help_text=_("Maximum discount that can be applied per single order."),
    )
    total_discount_capacity = MoneyField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        default_currency=None,
        help_text=_("Cumulative discount budget across all uses. Blank = unlimited."),
    )
    minimum_order_amount = MoneyField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        default_currency=None,
        help_text=_("Order must be at least this value for the code to apply."),
    )

    # ── Usage limits ──────────────────────────────────────────────────────────
    usage_limit = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_("Total times this code can be used by anyone."),
    )
    usage_limit_per_user = models.SmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_("Maximum times a single user may use this code."),
    )

    # ── Tracking ──────────────────────────────────────────────────────────────
    usages = models.PositiveIntegerField(
        default=0,
        help_text=_("Running count of redemptions."),
    )
    is_active = models.BooleanField(default=True, help_text=_("Master on/off switch."))

    objects = OffCodeManager()

    class Meta:
        verbose_name = _("Discount Code")
        verbose_name_plural = _("Discount Codes")
        ordering = ["-created"]
        constraints = [
            # Enforce mutual exclusivity at DB level
            models.CheckConstraint(
                condition=(
                    Q(discount_percent__isnull=True) | Q(fixed_discount_amount__isnull=True)
                ),
                name="offcode_one_discount_type",
            )
        ]

    def __str__(self) -> str:
        if self.fixed_discount_amount:
            discount_repr = str(self.fixed_discount_amount)
        else:
            discount_repr = f"{self.discount_percent}%"
        return f"{self.code} — {discount_repr}"

    # ── Lifecycle hooks (django-lifecycle) ────────────────────────────────────

    @hook(BEFORE_UPDATE, when="is_active", has_changed=True)
    def _on_active_toggle(self):
        """Log or emit signal when a code is deactivated/reactivated."""
        # Placeholder: attach signal / audit log here if needed.
        pass

    # ── Expiry checks (pure properties, zero DB queries) ──────────────────────

    @property
    def is_expired_by_time(self) -> bool:
        return bool(self.ends_at and timezone_now() > self.ends_at)

    @property
    def is_expired_by_total_uses(self) -> bool:
        return self.usage_limit is not None and self.usages >= self.usage_limit

    @property
    def is_expired_by_total_discount_cap(self) -> bool:
        if not (self.total_discount_capacity and self.total_discount_capacity.amount > 0):
            return False
        return self.total_discount_given >= self.total_discount_capacity.amount

    # ── Aggregate (single DB query) ───────────────────────────────────────────

    @property
    def total_discount_given(self) -> Decimal:
        """Sum of ``coupon_discount_amount`` across all orders using this code."""
        from ..catalog.models.order import Order  # late import — avoids circular dependency

        result = Order.objects.filter(off_code=self).aggregate(
            total=models.Sum("coupon_discount_amount")
        )["total"]
        return result if result is not None else Decimal("0")

    # ── Validity ──────────────────────────────────────────────────────────────

    @property
    def is_valid_for_general_check(self) -> bool:
        """Validity without any per-user context (used by manager finders)."""
        if not self.is_active:
            return False
        now = timezone_now()
        if self.starts_at and now < self.starts_at:
            return False
        return not (
            self.is_expired_by_time
            or self.is_expired_by_total_uses
            or self.is_expired_by_total_discount_cap
        )

    @property
    def is_valid(self) -> bool:
        """Alias for clarity — same as ``is_valid_for_general_check``."""
        return self.is_valid_for_general_check

    # ── Discount calculation ──────────────────────────────────────────────────

    def calculate_discount_amount(self, order_total: Decimal) -> Decimal:
        """
        Returns the discount to apply for *order_total* (same currency assumed).

        Caps applied in order:
        1. ``max_discount_per_use`` ceiling
        2. Cannot exceed the order total itself
        3. Minimum floor of 0

        Returns ``Decimal("0")`` when the code is invalid or has no discount.
        """
        if not self.is_valid:
            return Decimal("0")

        order_total = Decimal(str(order_total))

        if self.fixed_discount_amount:
            raw = Decimal(str(self.fixed_discount_amount.amount))
        elif self.discount_percent is not None:
            raw = order_total * (Decimal(str(self.discount_percent)) / Decimal("100"))
        else:
            return Decimal("0")

        if self.max_discount_per_use:
            raw = min(raw, Decimal(str(self.max_discount_per_use.amount)))

        return max(Decimal("0"), min(raw, order_total)).quantize(Decimal("0.01"))
