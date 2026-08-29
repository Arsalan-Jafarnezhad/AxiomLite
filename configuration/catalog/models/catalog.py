"""
catalog/models/catalog.py

Product catalog models: Category, Product, ProductComment.

Third-party deps used
─────────────────────
- django-money      pip install django-money
  MoneyField on price fields — stores amount + currency in two DB columns.

- django-model-utils  pip install django-model-utils
  TimeStampedModel  → ``created`` / ``modified`` auto timestamps
  SoftDeletableModel → ``is_removed`` flag + filtered default manager

- django-lifecycle  pip install django-lifecycle
  @hook decorators replace save()/delete() overrides with named, testable hooks.

- python-slugify    pip install python-slugify
  Unicode-aware slug generation (handles Farsi/Arabic names correctly).
"""

from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models.aggregates import Avg, Count
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

# django-model-utils
from model_utils.models import SoftDeletableModel, TimeStampedModel

# django-lifecycle
from django_lifecycle import (
    LifecycleModel,
    hook,
    BEFORE_CREATE,
    BEFORE_UPDATE,
    AFTER_DELETE,
    AFTER_UPDATE,
)

# django-money
from djmoney.models.fields import MoneyField
from djmoney.money import Money

# python-slugify (unicode-aware, handles non-Latin scripts)
from slugify import slugify as unicode_slugify

from catalog.constants import DATETIME_DISPLAY_FORMAT
from catalog.utils.file import get_product_image_path
from catalog.utils.formatting import format_money

User = get_user_model()


# ── Category ──────────────────────────────────────────────────────────────────

class Category(TimeStampedModel):
    """
    Hierarchical product category (self-referencing FK).

    Uses ``TimeStampedModel`` from django-model-utils for ``created`` /
    ``modified`` auto-timestamps instead of a custom ``BaseModel``.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = unicode_slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def full_path(self) -> str:
        """Returns breadcrumb-style path, e.g. ``Electronics > Laptops``."""
        parts = [self.name]
        node = self.parent
        while node:
            parts.insert(0, node.name)
            node = node.parent
        return " > ".join(parts)


# ── Product ───────────────────────────────────────────────────────────────────

class Product(LifecycleModel, SoftDeletableModel, TimeStampedModel):
    """
    A sellable product.

    Pricing
    ───────
    ``price`` is a ``MoneyField`` — it stores both the decimal amount and the
    ISO 4217 currency code.  Reading ``product.price`` returns a ``Money``
    object (``product.price.amount``, ``product.price.currency``).

    ``final_price`` is a Python-computed property (not a DB generated column)
    because ``MoneyField`` amounts are Decimal values — the DB expression
    approach would require casting that varies by backend.  The trade-off is
    one extra Python operation on access, which is acceptable.

    Slug generation
    ───────────────
    Uses ``python-slugify`` for proper Unicode (Farsi / Arabic) handling.
    Duplicate slugs get a numeric suffix appended.
    """

    class Status(models.IntegerChoices):
        DISABLED     = 0, _("Disabled")
        ENABLED      = 1, _("Enabled")
        SOLD_OUT     = 2, _("Sold Out")
        DISCONTINUED = 3, _("Discontinued")

    # ── Core ─────────────────────────────────────────────────────────────────
    name        = models.CharField(max_length=255)
    slug        = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField(max_length=2048)

    # ── Relations ─────────────────────────────────────────────────────────────
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Seller"),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
    )

    # ── Media ─────────────────────────────────────────────────────────────────
    image = models.ImageField(
        upload_to=get_product_image_path,
        null=True,
        blank=True,
        default="default-product-image.png",
    )

    # ── Pricing (MoneyField) ──────────────────────────────────────────────────
    # Each MoneyField creates TWO database columns:
    #   price              → DecimalField
    #   price_currency     → CharField(max_length=3)
    price = MoneyField(
        max_digits=16,
        decimal_places=2,
        default_currency="IRR",
        validators=[MinValueValidator(Money(0, "IRR"))],
        help_text=_("Base price of the product."),
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0"),
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("100")),
        ],
        help_text=_("Discount percentage (0–100)."),
    )

    # ── Inventory ─────────────────────────────────────────────────────────────
    stock  = models.PositiveIntegerField(default=0)
    status = models.SmallIntegerField(
        choices=Status.choices,
        default=Status.ENABLED,
    )

    # ── Counters (denormalised) ───────────────────────────────────────────────
    views         = models.PositiveIntegerField(default=0, editable=False)
    selling_count = models.PositiveBigIntegerField(default=0, editable=False)

    # ── Rating (maintained by update_rating_stats) ────────────────────────────
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal("0"),
        editable=False,
    )
    rating_count = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        verbose_name        = _("Product")
        verbose_name_plural = _("Products")
        ordering            = ["-created"]
        indexes             = [
            models.Index(fields=["status", "stock"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return self.name

    # ── django-lifecycle hooks ────────────────────────────────────────────────

    @hook(BEFORE_CREATE)
    @hook(BEFORE_UPDATE, when="name", has_changed=True)
    def _auto_slug(self) -> None:
        """
        Generates a URL-safe, Unicode-aware slug from the product name.
        Appends a numeric suffix to prevent uniqueness collisions.
        """
        base = unicode_slugify(self.name, allow_unicode=False)
        slug = base
        counter = 1
        qs = Product.objects.exclude(pk=self.pk)
        while qs.filter(slug=slug).exists():
            slug = f"{base}-{counter}"
            counter += 1
        self.slug = slug

    # ── Computed properties ───────────────────────────────────────────────────

    @property
    def discount_amount(self) -> Money:
        """Discount in the same currency as the price."""
        amount = (self.price.amount * self.discount_percentage / Decimal("100")).quantize(
            Decimal("0.01")
        )
        return Money(amount, self.price.currency)

    @property
    def final_price(self) -> Money:
        """Price after discount."""
        return Money(
            (self.price.amount - self.discount_amount.amount).quantize(Decimal("0.01")),
            self.price.currency,
        )

    @property
    def has_discount(self) -> bool:
        return self.discount_percentage > 0

    @property
    def is_in_stock(self) -> bool:
        return self.stock > 0

    def is_available(self) -> bool:
        return (
            self.status == self.Status.ENABLED
            and self.is_in_stock
            and not self.is_removed
        )

    # ── Display helpers ───────────────────────────────────────────────────────

    @property
    def price_display(self) -> str:
        return format_money(self.price)

    @property
    def final_price_display(self) -> str:
        return format_money(self.final_price)

    @property
    def discount_percentage_display(self) -> str:
        return f"{self.discount_percentage:.0f}%"

    @property
    def created_at_display(self) -> str:
        return self.created.strftime(DATETIME_DISPLAY_FORMAT)

    @property
    def status_class(self) -> str:
        return {0: "error", 1: "success", 2: "warning", 3: "error"}.get(self.status, "error")

    @property
    def panel_url(self) -> str:
        return reverse("catalog:product-detail-panel", kwargs={"slug": self.slug})

    @property
    def absolute_url(self) -> str:
        return reverse("catalog:product-detail", kwargs={"slug": self.slug})

    # ── Rating stats ──────────────────────────────────────────────────────────

    def update_rating_stats(self) -> None:
        """
        Recalculates ``average_rating`` and ``rating_count`` from the live
        comment set and persists them.

        Deferred to post-commit via ``transaction.on_commit`` so the stats
        reflect the committed state rather than the in-progress transaction.
        """
        pk = self.pk  # capture — self may be stale by commit time

        def _do_update():
            agg = ProductComment.objects.filter(
                product_id=pk, rating__isnull=False
            ).aggregate(avg=Avg("rating"), cnt=Count("rating"))
            Product.objects.filter(pk=pk).update(
                average_rating=round(agg["avg"] or 0, 1),
                rating_count=agg["cnt"] or 0,
            )

        transaction.on_commit(_do_update)


# ── ProductComment ────────────────────────────────────────────────────────────

class ProductComment(LifecycleModel, SoftDeletableModel, TimeStampedModel):
    """User-submitted review with optional 1–5 star rating."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="product_comments",
    )
    text   = models.TextField()
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name        = _("Product Comment")
        verbose_name_plural = _("Product Comments")
        ordering            = ["-created"]

    def __str__(self) -> str:
        return f"Comment by {self.user} on {self.product}"

    # ── Lifecycle hooks ───────────────────────────────────────────────────────

    @hook(AFTER_UPDATE)
    @hook(AFTER_DELETE)
    def _refresh_product_rating(self) -> None:
        """Triggers rating stats recalculation whenever a comment changes."""
        self.product.update_rating_stats()

    # django-lifecycle fires AFTER_DELETE before the DB row is gone when using
    # soft-delete, but we also hook the hard-delete path:
    def delete(self, *args, **kwargs) -> None:
        product = self.product
        super().delete(*args, **kwargs)
        if product:
            product.update_rating_stats()
