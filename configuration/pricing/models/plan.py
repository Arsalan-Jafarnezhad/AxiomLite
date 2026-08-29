"""
pricing/models/plan.py

The core pricing tier (e.g. "Starter", "Pro", "Enterprise").
"""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from djmoney.models.fields import MoneyField
from djmoney.money import Money

from .base import ActiveQuerySet


class Plan(models.Model):
    """A sellable pricing tier, with its features/attributes as related sets."""

    class BillingType(models.TextChoices):
        FIXED = "fixed", _("Fixed Price")
        HOURLY = "hourly", _("Hourly")
        MONTHLY = "monthly", _("Monthly")
        YEARLY = "yearly", _("Yearly")
        CUSTOM = "custom", _("Custom")

    # Billing types that repeat on a schedule vs. a one-off charge — used by
    # `is_recurring` below instead of hardcoding the check at every call site.
    RECURRING_BILLING_TYPES = {BillingType.MONTHLY, BillingType.YEARLY}

    name = models.CharField(_("Name"), max_length=100)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)
    short_description = models.CharField(_("Short description"), max_length=200, blank=True)
    description = models.TextField(_("Description"), blank=True)

    starting_price = MoneyField(
        _("Starting price"),
        max_digits=12,
        decimal_places=2,
        default_currency="USD",
        validators=[MinValueValidator(Money(0, "USD"))],
    )
    billing_type = models.CharField(
        _("Billing type"),
        max_length=20,
        choices=BillingType.choices,
        default=BillingType.FIXED,
        db_index=True,
    )

    badge = models.CharField(
        _("Badge"), max_length=40, blank=True, help_text=_("Popular, Best Value, New, ...")
    )
    icon = models.CharField(_("Icon"), max_length=50, blank=True, help_text=_("Material Symbols icon name"))

    featured = models.BooleanField(_("Featured"), default=False, db_index=True)
    active = models.BooleanField(_("Active"), default=True, db_index=True)
    order = models.PositiveSmallIntegerField(_("Order"), default=0, db_index=True)

    estimated_delivery_days = models.PositiveSmallIntegerField(
        _("Estimated delivery (days)"), null=True, blank=True
    )
    revisions = models.PositiveSmallIntegerField(_("Revisions"), default=3)
    support_days = models.PositiveSmallIntegerField(_("Support (days)"), default=30)

    button_text = models.CharField(_("Button text"), max_length=50, default="Get Started")
    button_url = models.URLField(_("Button URL"), blank=True)

    meta_title = models.CharField(_("Meta title"), max_length=200, blank=True)
    meta_description = models.CharField(_("Meta description"), max_length=300, blank=True)

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    objects = ActiveQuerySet.as_manager()

    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("Plans")
        ordering = ("order", "id")
        indexes = [models.Index(fields=["active", "featured", "order"])]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self) -> str:
        base = slugify(self.name)
        slug = base
        suffix = 1
        qs = Plan.objects.exclude(pk=self.pk)
        while qs.filter(slug=slug).exists():
            suffix += 1
            slug = f"{base}-{suffix}"
        return slug

    # ── Convenience accessors ─────────────────────────────────────────────

    @property
    def is_recurring(self) -> bool:
        return self.billing_type in self.RECURRING_BILLING_TYPES

    @property
    def billing_suffix(self) -> str:
        """e.g. '/mo' for monthly, '/yr' for yearly, '' otherwise."""
        return {
            self.BillingType.MONTHLY: _("/mo"),
            self.BillingType.YEARLY: _("/yr"),
            self.BillingType.HOURLY: _("/hr"),
        }.get(self.billing_type, "")

    @property
    def price_display(self) -> str:
        return f"{self.starting_price} {self.billing_suffix}".strip()

    @property
    def included_features(self):
        """Only the features actually included in this plan, in display order."""
        return self.features.filter(included=True)

    @property
    def highlighted_features(self):
        return self.features.filter(included=True, highlight=True)

    def get_absolute_url(self) -> str:
        return reverse("pricing:plan-detail", kwargs={"slug": self.slug})
