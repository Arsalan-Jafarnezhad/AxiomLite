"""
catalog/models/payment.py

Payment model — tracks a single payment attempt per Order.

Currency routing
────────────────
``Payment.get_payment_route()`` returns a :class:`~catalog.payment_gateway.PaymentRoute`
that tells the view whether to redirect to:

    - Zarinpal (IRR / IRR orders)
    - ``catalog/templates/catalog/payment_internal.html`` (all other currencies)

Third-party deps used
─────────────────────
- django-money        MoneyField for ``amount``
- django-model-utils  TimeStampedModel, SoftDeletableModel
- django-lifecycle    @hook decorators
"""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from model_utils.models import SoftDeletableModel, TimeStampedModel
from django_lifecycle import LifecycleModel, hook, BEFORE_CREATE

from djmoney.models.fields import MoneyField
from djmoney.money import Money

from catalog.constants import DATETIME_DISPLAY_FORMAT
from catalog.utils.formatting import format_money
from catalog.utils.id import generate_key
from catalog.utils.payment_gateway import PaymentRoute, resolve_payment_route


class Payment(LifecycleModel, SoftDeletableModel, TimeStampedModel):
    """
    Records one payment attempt for an Order.

    One Order → One Payment (``OneToOneField``).
    Multiple *attempts* are represented by updating status + timestamps on
    the same Payment row rather than creating new rows — keeps the model
    simple and avoids orphaned payment records.
    """

    class Status(models.IntegerChoices):
        PENDING   = 0, _("Pending")
        SUCCESS   = 1, _("Success")
        FAILED    = 2, _("Failed")
        REFUNDED  = 3, _("Refunded")
        CANCELLED = 4, _("Cancelled")

    class PaymentMethod(models.TextChoices):
        ZARINPAL         = "ZARINPAL",         _("ZarinPal")
        INTERNAL         = "INTERNAL",         _("Internal Gateway")
        BANK_TRANSFER    = "BANK_TRANSFER",    _("Bank Transfer")
        CASH_ON_DELIVERY = "CASH_ON_DELIVERY", _("Cash on Delivery")

    # ── Relations ─────────────────────────────────────────────────────────────
    order = models.OneToOneField(
        "catalog.Order",
        on_delete=models.CASCADE,
        related_name="payment",
    )

    # ── Core ─────────────────────────────────────────────────────────────────
    description = models.TextField(
        max_length=1024,
        default=_("Purchase from our website"),
    )
    status = models.SmallIntegerField(
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # MoneyField → two DB columns: amount + amount_currency
    amount = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency="IRR",
        help_text=_("Total amount charged."),
    )
    value_added_tax = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("10"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text=_("VAT percentage (e.g. 10 for 10%)."),
    )
    payment_method = models.CharField(
        max_length=50,
        choices=PaymentMethod.choices,
        blank=True,
        null=True,
    )

    # ── Identifiers ───────────────────────────────────────────────────────────
    payment_id = models.CharField(
        max_length=39,
        unique=True,
        default=generate_key,
        editable=False,
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
        help_text=_("Gateway-assigned transaction ID."),
    )
    authority = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
        db_index=True,
        help_text=_("Zarinpal authority token."),
    )

    # ── Network context ───────────────────────────────────────────────────────
    user_ip_address = models.GenericIPAddressField(
        unpack_ipv4=True,
        blank=True,
        null=True,
        db_index=True,
    )
    gateway_response = models.TextField(
        blank=True,
        help_text=_("Raw JSON response from the payment gateway."),
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    payment_request_time = models.DateTimeField(null=True, blank=True)
    paid_at              = models.DateTimeField(null=True, blank=True)
    refunded_at          = models.DateTimeField(null=True, blank=True)
    cancelled_at         = models.DateTimeField(null=True, blank=True)
    failed_at            = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name        = _("Payment")
        verbose_name_plural = _("Payments")
        ordering            = ["-created"]

    def __str__(self) -> str:
        return f"Payment {self.payment_id} — {self.get_status_display()}"

    # ── Lifecycle hooks ───────────────────────────────────────────────────────

    @hook(BEFORE_CREATE)
    def _inherit_order_currency(self) -> None:
        """
        Copies the order's currency onto the payment's ``amount`` field
        when the Payment is first created, ensuring no currency mismatch.
        """
        if self.order_id and self.amount:
            currency = self.order.currency
            self.amount = Money(self.amount.amount, currency)

    # ── Payment routing ───────────────────────────────────────────────────────

    def get_payment_route(self) -> PaymentRoute:
        """
        Returns a :class:`~catalog.payment_gateway.PaymentRoute` describing
        where the user should be directed to complete payment.

        Usage in a view::

            route = payment.get_payment_route()
            if route.use_zarinpal:
                result = payment_request(amount, description, callback, request)
                return redirect(result["redirect_url"])
            else:
                return redirect(route.redirect_url)
        """
        currency = str(self.amount.currency)
        return resolve_payment_route(currency, self.payment_id)

    # ── Display helpers ───────────────────────────────────────────────────────

    @property
    def amount_display(self) -> str:
        return format_money(self.amount)

    @property
    def vat_amount(self) -> Money:
        vat = (self.amount.amount * self.value_added_tax / Decimal("100")).quantize(
            Decimal("0.01")
        )
        return Money(vat, self.amount.currency)

    @property
    def vat_amount_display(self) -> str:
        return format_money(self.vat_amount)

    @property
    def status_class(self) -> str:
        return {0: "warning", 1: "success", 2: "error", 3: "warning", 4: "error"}.get(
            self.status, "warning"
        )

    @property
    def status_date(self):
        """Most relevant timestamp for the current status."""
        return {
            self.Status.PENDING:   self.created,
            self.Status.SUCCESS:   self.paid_at,
            self.Status.FAILED:    self.failed_at,
            self.Status.REFUNDED:  self.refunded_at,
            self.Status.CANCELLED: self.cancelled_at,
        }.get(self.status)

    @property
    def status_date_display(self) -> str:
        dt = self.status_date
        return dt.strftime(DATETIME_DISPLAY_FORMAT) if dt else "—"

    @property
    def absolute_url(self) -> str:
        return reverse("catalog:payment-detail-panel", kwargs={"payment_id": self.payment_id})

    @property
    def is_iranian_currency(self) -> bool:
        """Convenience flag — ``True`` when this payment will go to Zarinpal."""
        return str(self.amount.currency) in {"IRR", "IRR"}
