"""
catalog/admin/filters.py

Reusable admin filters for the catalog application.
Compatible with Django Admin and Django Unfold.
"""

from __future__ import annotations

from django.contrib import admin
from django.utils import timezone

# =============================================================================
# Soft Delete
# =============================================================================


class SoftDeleteFilter(admin.SimpleListFilter):
    title = "Deleted"
    parameter_name = "deleted"

    def lookups(self, request, model_admin):
        return (
            ("active", "Active"),
            ("deleted", "Deleted"),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value == "active":
            return queryset.filter(is_removed=False)

        if value == "deleted":
            return queryset.filter(is_removed=True)

        return queryset


# =============================================================================
# Discount
# =============================================================================


class DiscountFilter(admin.SimpleListFilter):
    title = "Discount"
    parameter_name = "discount"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Has Discount"),
            ("no", "No Discount"),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value == "yes":
            return queryset.filter(discount_percentage__gt=0)

        if value == "no":
            return queryset.filter(discount_percentage=0)

        return queryset


# =============================================================================
# Stock
# =============================================================================


class StockFilter(admin.SimpleListFilter):
    title = "Stock"
    parameter_name = "stock"

    def lookups(self, request, model_admin):
        return (
            ("available", "In Stock"),
            ("empty", "Out of Stock"),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value == "available":
            return queryset.filter(stock__gt=0)

        if value == "empty":
            return queryset.filter(stock=0)

        return queryset


# =============================================================================
# Rating
# =============================================================================


class RatingFilter(admin.SimpleListFilter):
    title = "Rating"
    parameter_name = "rating"

    def lookups(self, request, model_admin):
        return (
            ("5", "5★"),
            ("4", "4★ & Up"),
            ("3", "3★ & Up"),
            ("0", "No Rating"),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value == "5":
            return queryset.filter(average_rating=5)

        if value == "4":
            return queryset.filter(average_rating__gte=4)

        if value == "3":
            return queryset.filter(average_rating__gte=3)

        if value == "0":
            return queryset.filter(rating_count=0)

        return queryset


# =============================================================================
# Coupon Validity
# =============================================================================


class CouponValidityFilter(admin.SimpleListFilter):
    title = "Validity"
    parameter_name = "validity"

    def lookups(self, request, model_admin):
        return (
            ("valid", "Valid"),
            ("expired", "Expired"),
            ("inactive", "Inactive"),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        value = self.value()

        if value == "valid":
            return queryset.filter(
                is_active=True,
            ).exclude(
                ends_at__lt=now,
            )

        if value == "expired":
            return queryset.filter(
                ends_at__lt=now,
            )

        if value == "inactive":
            return queryset.filter(
                is_active=False,
            )

        return queryset


# =============================================================================
# Payment Success
# =============================================================================


class PaymentStatusFilter(admin.SimpleListFilter):
    title = "Payment"
    parameter_name = "payment"

    def lookups(self, request, model_admin):
        return (
            ("pending", "Pending"),
            ("success", "Success"),
            ("failed", "Failed"),
            ("refunded", "Refunded"),
            ("cancelled", "Cancelled"),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value is None:
            return queryset

        return queryset.filter(status=value)


# =============================================================================
# Order Amount
# =============================================================================


class OrderAmountFilter(admin.SimpleListFilter):
    title = "Amount"
    parameter_name = "amount"

    def lookups(self, request, model_admin):
        return (
            ("small", "< 1M"),
            ("medium", "1M - 10M"),
            ("large", "> 10M"),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value == "small":
            return queryset.filter(final_amount__lt=1_000_000)

        if value == "medium":
            return queryset.filter(
                final_amount__gte=1_000_000,
                final_amount__lte=10_000_000,
            )

        if value == "large":
            return queryset.filter(
                final_amount__gt=10_000_000,
            )

        return queryset


# =============================================================================
# Has Image
# =============================================================================


class HasImageFilter(admin.SimpleListFilter):
    title = "Image"
    parameter_name = "image"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Has Image"),
            ("no", "No Image"),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value == "yes":
            return queryset.exclude(image="")

        if value == "no":
            return queryset.filter(image="")

        return queryset


# =============================================================================
# Comment Rating
# =============================================================================


class CommentRatingFilter(admin.SimpleListFilter):
    title = "Rating"

    parameter_name = "rating"

    def lookups(self, request, model_admin):
        return (
            ("5", "★★★★★"),
            ("4", "★★★★"),
            ("3", "★★★"),
            ("2", "★★"),
            ("1", "★"),
            ("none", "No Rating"),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value == "none":
            return queryset.filter(rating__isnull=True)

        if value:
            return queryset.filter(rating=int(value))

        return queryset
