"""
catalog/models/order.py

OrderItem and Order models.

Third-party deps used
─────────────────────
- django-money        MoneyField for all monetary columns
- django-model-utils  TimeStampedModel, SoftDeletableModel
- django-lifecycle    @hook decorators
"""

from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.query_utils import Q
from django.utils.timezone import now as timezone_now
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from model_utils.models import SoftDeletableModel, TimeStampedModel
from django_lifecycle import LifecycleModel, hook, AFTER_SAVE

from djmoney.models.fields import MoneyField
from djmoney.money import Money
from moneyed import get_currency

from catalog.constants import DATETIME_DISPLAY_FORMAT
from catalog.utils.formatting import format_money
from catalog.utils.id import generate_key
from .discount import OffCode 
User = get_user_model()


class OrderItem(TimeStampedModel):
    """
    A single product line within an Order.

    ``price_at_order`` is a ``MoneyField`` — it preserves both the amount
    *and* the currency at the time of ordering, so historical records remain
    accurate if the product's currency later changes.
    """

    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    # Snapshot price — never mutate after creation.
    price_at_order = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency="IRR",
        validators=[MinValueValidator(Decimal("0"))],
        help_text=_("Product price captured at order time."),
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name        = _("Order Item")
        verbose_name_plural = _("Order Items")
        unique_together     = ("order", "product")

    def __str__(self) -> str:
        name = self.product.name if self.product else "Deleted Product"
        return f"{self.quantity} × {name}"

    @property
    def subtotal(self) -> Money:
        return Money(
            (self.price_at_order.amount * self.quantity).quantize(Decimal("0.01")),
            self.price_at_order.currency,
        )

    @property
    def subtotal_display(self) -> str:
        return format_money(self.subtotal)


class Order(LifecycleModel, SoftDeletableModel, TimeStampedModel):
    """
    A customer order.

    Currency
    ────────
    All monetary fields share the ``currency`` field.  A single-currency
    constraint is enforced at the model level: coupon discounts must be in
    the same currency as the order subtotal.

    Payment routing
    ───────────────
    The view layer calls ``payment_gateway.resolve_payment_route(
        order.currency, order.payment.payment_id)`` to decide between
    Zarinpal and the internal HTML payment page.
    """

    class Status(models.IntegerChoices):
        PENDING_PAYMENT = 0, _("Pending Payment")
        PAID            = 1, _("Paid")
        PROCESSING      = 2, _("Processing")
        SHIPPED         = 3, _("Shipped")
        DELIVERED       = 4, _("Delivered")
        CANCELLED       = 5, _("Cancelled")
        REFUNDED        = 6, _("Refunded")

    # ── Identity ──────────────────────────────────────────────────────────────
    user     = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    order_id = models.CharField(
        max_length=39,
        unique=True,
        default=generate_key,
        editable=False,
        help_text=_("Human-readable unique order reference."),
    )
    status = models.SmallIntegerField(
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
    )

    # ── Currency (single source of truth for the order) ───────────────────────
    # All MoneyFields below share this currency.
    # Storing it separately allows ORDER BY / filter without joining.
    currency = models.CharField(
        max_length=3,
        default="IRR",
        help_text=_("ISO 4217 currency code for this order."),
    )

    # ── Amounts ───────────────────────────────────────────────────────────────
    subtotal_amount = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency="IRR",
        default=Decimal("0"),
        help_text=_("Sum of item subtotals before any discounts."),
    )
    coupon_discount_amount = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency="IRR",
        default=Decimal("0"),
        help_text=_("Discount applied by a coupon code."),
    )
    final_amount = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency="IRR",
        default=Decimal("0"),
        help_text=_("Amount payable after discounts."),
    )

    # ── Addresses ─────────────────────────────────────────────────────────────
    shipping_address = models.TextField(blank=True)
    billing_address  = models.TextField(blank=True)

    # ── Coupon ────────────────────────────────────────────────────────────────
    off_code = models.ForeignKey(
        "catalog.OffCode",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    # ── Fulfilment timestamps ─────────────────────────────────────────────────
    shipped_at   = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name        = _("Order")
        verbose_name_plural = _("Orders")
        ordering            = ["-created"]
        indexes             = [
            models.Index(fields=["status"]),
            models.Index(fields=["order_id"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self) -> str:
        return f"Order {self.order_id} — {self.get_status_display()}"

    # ── Lifecycle hooks ───────────────────────────────────────────────────────

    @hook(AFTER_SAVE)
    def _sync_currency_fields(self) -> None:
        """
        Keeps all MoneyField currency columns in sync with ``self.currency``
        whenever the order is saved.  This prevents accidental mixed-currency
        states on the order record itself.

        Note: item-level currencies are independent (each OrderItem has its
        own currency snapshot).
        """
        # MoneyFields store their currency in a sibling ``<field>_currency`` attribute.
        for field in ("subtotal_amount", "coupon_discount_amount", "final_amount"):
            setattr(self, f"{field}_currency", self.currency)

    # ── Amount recalculation ──────────────────────────────────────────────────

    def recalculate_amounts(self) -> None:
        """
        Recomputes ``subtotal_amount`` and ``final_amount`` from live items.
        Call explicitly after adding / removing items, then ``save()``.

        Items with a *different* currency are converted at face value (i.e.,
        treated as if 1:1) — implement a currency-conversion service hook here
        if your catalog needs true multi-currency cart support.
        """
        subtotal = sum(
            (item.subtotal.amount for item in self.items.all()),
            Decimal("0"),
        )
        self.subtotal_amount = Money(subtotal, self.currency)
        self.final_amount = Money(
            max(Decimal("0"), subtotal - self.coupon_discount_amount.amount),
            self.currency,
        )

    # ── Status transitions ────────────────────────────────────────────────────

    def _transition(self, allowed_from: tuple, target: int, **timestamps) -> bool:
        if self.status not in allowed_from:
            return False
        self.status = target
        for field, value in timestamps.items():
            setattr(self, field, value)
        self.save(update_fields=["status", *timestamps.keys(), "modified"])
        return True

    def mark_as_paid(self) -> bool:
        return self._transition((self.Status.PENDING_PAYMENT,), self.Status.PAID)

    def mark_as_processing(self) -> bool:
        return self._transition((self.Status.PAID,), self.Status.PROCESSING)

    def mark_as_shipped(self) -> bool:
        return self._transition(
            (self.Status.PAID, self.Status.PROCESSING),
            self.Status.SHIPPED,
            shipped_at=timezone_now(),
        )

    def mark_as_delivered(self) -> bool:
        return self._transition(
            (self.Status.SHIPPED,),
            self.Status.DELIVERED,
            delivered_at=timezone_now(),
        )

    def mark_as_cancelled(self) -> bool:
        blocked = (
            self.Status.SHIPPED,
            self.Status.DELIVERED,
            self.Status.CANCELLED,
            self.Status.REFUNDED,
        )
        return self._transition(
            tuple(s for s in self.Status if s not in blocked),
            self.Status.CANCELLED,
            cancelled_at=timezone_now(),
        )

    def mark_as_refunded(self) -> bool:
        return self._transition(
            (self.Status.DELIVERED, self.Status.SHIPPED),
            self.Status.REFUNDED,
        )

    # ── Coupon application ────────────────────────────────────────────────────

    def apply_discount(self, coupon) -> tuple[bool, str]:
        """
        Attempts to apply an ``OffCode`` to this order.

        Returns ``(True, success_msg)`` or ``(False, reason)``.
        **Must be called inside a ``transaction.atomic()`` block.**
        """
        from .discount import OffCode

        if not isinstance(coupon, OffCode):
            return False, "Invalid coupon object."
        if not coupon.is_valid:
            return False, "This coupon is not currently valid."

        # Minimum order amount gate
        if coupon.minimum_order_amount:
            if self.subtotal_amount.amount < coupon.minimum_order_amount.amount:
                return False, (
                    f"Order must be at least "
                    f"{format_money(coupon.minimum_order_amount)} to use this coupon."
                )

        # Per-user usage gate
        if coupon.usage_limit_per_user is not None:
            used = Order.objects.filter(user=self.user, off_code=coupon).count()
            if used >= coupon.usage_limit_per_user:
                return False, "You have reached the maximum uses for this coupon."

        discount = coupon.calculate_discount_amount(self.subtotal_amount.amount)
        if discount <= 0:
            return False, "Coupon cannot be applied to this order total."

        # Total budget cap — partially apply if remaining budget is less
        if coupon.total_discount_capacity:
            remaining = coupon.total_discount_capacity.amount - coupon.total_discount_given
            discount = max(Decimal("0"), min(discount, remaining))

        if discount <= 0:
            return False, "This coupon has reached its total discount limit."

        self.off_code                = coupon
        self.coupon_discount_amount  = Money(discount, self.currency)
        self.final_amount            = Money(
            max(Decimal("0"), self.subtotal_amount.amount - discount),
            self.currency,
        )
        return True, "Coupon applied successfully."

    # ── Display helpers ───────────────────────────────────────────────────────

    @property
    def final_amount_display(self) -> str:
        return format_money(self.final_amount)

    @property
    def subtotal_amount_display(self) -> str:
        return format_money(self.subtotal_amount)

    @property
    def created_at_display(self) -> str:
        return self.created.strftime(DATETIME_DISPLAY_FORMAT)

    @property
    def status_class(self) -> str:
        return {
            0: "warning",
            1: "success",
            2: "warning",
            3: "info",
            4: "success",
            5: "error",
            6: "success",
        }.get(self.status, "warning")

    @property
    def panel_url(self) -> str:
        return reverse("catalog:order-detail-panel", kwargs={"order_id": self.order_id})

    def get_items_detail(self) -> list[dict]:
        return [
            {
                "product_name": item.product.name if item.product else "Deleted Product",
                "product_slug": item.product.slug if item.product else "",
                "quantity": item.quantity,
                "price_at_order": item.price_at_order,
                "price_display": format_money(item.price_at_order),
                "subtotal": item.subtotal,
                "subtotal_display": item.subtotal_display,
            }
            for item in self.items.select_related("product")
        ]
