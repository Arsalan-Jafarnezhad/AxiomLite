"""
catalog/admin/actions.py

Reusable admin actions for Django Unfold.

These actions are intentionally generic so they can be shared between
ProductAdmin, OrderAdmin, OffCodeAdmin, PaymentAdmin, etc.
"""

from __future__ import annotations

from django.contrib import admin, messages
from django.db import transaction
from django.utils.translation import gettext_lazy as _

# ----------------------------------------------------------------------
# Generic Boolean Actions
# ----------------------------------------------------------------------


@admin.action(description=_("Enable selected objects"))
def enable_objects(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)

    modeladmin.message_user(
        request,
        _("Successfully enabled %(count)s object(s).")
        % {
            "count": updated,
        },
        messages.SUCCESS,
    )


@admin.action(description=_("Disable selected objects"))
def disable_objects(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)

    modeladmin.message_user(
        request,
        _("Successfully disabled %(count)s object(s).")
        % {
            "count": updated,
        },
        messages.WARNING,
    )


# ----------------------------------------------------------------------
# Soft Delete
# ----------------------------------------------------------------------


@admin.action(description=_("Soft delete selected objects"))
def soft_delete_objects(modeladmin, request, queryset):
    count = 0

    with transaction.atomic():
        for obj in queryset:
            obj.delete()
            count += 1

    modeladmin.message_user(
        request,
        _("Soft deleted %(count)s object(s).")
        % {
            "count": count,
        },
        messages.SUCCESS,
    )


@admin.action(description=_("Restore selected objects"))
def restore_objects(modeladmin, request, queryset):
    updated = queryset.update(is_removed=False)

    modeladmin.message_user(
        request,
        _("Restored %(count)s object(s).")
        % {
            "count": updated,
        },
        messages.SUCCESS,
    )


# ----------------------------------------------------------------------
# Product Status Actions
# ----------------------------------------------------------------------


@admin.action(description=_("Enable selected products"))
def enable_products(modeladmin, request, queryset):
    updated = queryset.update(status=1)

    modeladmin.message_user(
        request,
        _("Enabled %(count)s products.")
        % {
            "count": updated,
        },
        messages.SUCCESS,
    )


@admin.action(description=_("Disable selected products"))
def disable_products(modeladmin, request, queryset):
    updated = queryset.update(status=0)

    modeladmin.message_user(
        request,
        _("Disabled %(count)s products.")
        % {
            "count": updated,
        },
        messages.WARNING,
    )


@admin.action(description=_("Mark as Sold Out"))
def mark_products_sold_out(modeladmin, request, queryset):
    updated = queryset.update(status=2)

    modeladmin.message_user(
        request,
        _("Updated %(count)s products.")
        % {
            "count": updated,
        },
        messages.SUCCESS,
    )


@admin.action(description=_("Mark as Discontinued"))
def mark_products_discontinued(modeladmin, request, queryset):
    updated = queryset.update(status=3)

    modeladmin.message_user(
        request,
        _("Updated %(count)s products.")
        % {
            "count": updated,
        },
        messages.WARNING,
    )


# ----------------------------------------------------------------------
# Order Actions
# ----------------------------------------------------------------------


@admin.action(description=_("Mark selected orders as Paid"))
def mark_orders_paid(modeladmin, request, queryset):
    success = 0

    for order in queryset:
        if order.mark_as_paid():
            success += 1

    modeladmin.message_user(
        request,
        _("Successfully updated %(count)s order(s).")
        % {
            "count": success,
        },
        messages.SUCCESS,
    )


@admin.action(description=_("Mark selected orders as Processing"))
def mark_orders_processing(modeladmin, request, queryset):
    success = 0

    for order in queryset:
        if order.mark_as_processing():
            success += 1

    modeladmin.message_user(
        request,
        _("Successfully updated %(count)s order(s).")
        % {
            "count": success,
        },
        messages.SUCCESS,
    )


@admin.action(description=_("Mark selected orders as Shipped"))
def mark_orders_shipped(modeladmin, request, queryset):
    success = 0

    for order in queryset:
        if order.mark_as_shipped():
            success += 1

    modeladmin.message_user(
        request,
        _("Successfully updated %(count)s order(s).")
        % {
            "count": success,
        },
        messages.SUCCESS,
    )


@admin.action(description=_("Mark selected orders as Delivered"))
def mark_orders_delivered(modeladmin, request, queryset):
    success = 0

    for order in queryset:
        if order.mark_as_delivered():
            success += 1

    modeladmin.message_user(
        request,
        _("Successfully updated %(count)s order(s).")
        % {
            "count": success,
        },
        messages.SUCCESS,
    )


@admin.action(description=_("Cancel selected orders"))
def mark_orders_cancelled(modeladmin, request, queryset):
    success = 0

    for order in queryset:
        if order.mark_as_cancelled():
            success += 1

    modeladmin.message_user(
        request,
        _("Cancelled %(count)s order(s).")
        % {
            "count": success,
        },
        messages.WARNING,
    )


@admin.action(description=_("Refund selected orders"))
def mark_orders_refunded(modeladmin, request, queryset):
    success = 0

    for order in queryset:
        if order.mark_as_refunded():
            success += 1

    modeladmin.message_user(
        request,
        _("Refunded %(count)s order(s).")
        % {
            "count": success,
        },
        messages.SUCCESS,
    )


# ----------------------------------------------------------------------
# Coupons
# ----------------------------------------------------------------------


@admin.action(description=_("Activate selected discount codes"))
def activate_offcodes(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)

    modeladmin.message_user(
        request,
        _("Activated %(count)s discount code(s).")
        % {
            "count": updated,
        },
        messages.SUCCESS,
    )


@admin.action(description=_("Deactivate selected discount codes"))
def deactivate_offcodes(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)

    modeladmin.message_user(
        request,
        _("Deactivated %(count)s discount code(s).")
        % {
            "count": updated,
        },
        messages.WARNING,
    )


from copy import deepcopy

from django.contrib import admin, messages
from django.db import transaction

from catalog.models import Product

# ==========================================================
# Duplicate Products
# ==========================================================


@admin.action(description="Duplicate selected products")
def duplicate_products(modeladmin, request, queryset):

    created = 0

    with transaction.atomic():

        for product in queryset:

            old_pk = product.pk

            product.pk = None
            product.slug = ""
            product.views = 0
            product.selling_count = 0
            product.average_rating = 0
            product.rating_count = 0

            product.save()

            created += 1

    modeladmin.message_user(
        request,
        f"{created} product(s) duplicated.",
        messages.SUCCESS,
    )


# ==========================================================
# Regenerate Slugs
# ==========================================================


@admin.action(description="Regenerate slugs")
def regenerate_product_slugs(modeladmin, request, queryset):

    for product in queryset:
        product.slug = ""
        product.save(update_fields=["name", "slug"])

    modeladmin.message_user(
        request,
        f"{queryset.count()} slug(s) regenerated.",
        messages.SUCCESS,
    )


# ==========================================================
# Recalculate Ratings
# ==========================================================


@admin.action(description="Recalculate ratings")
def recalculate_product_ratings(modeladmin, request, queryset):

    for product in queryset:
        product.update_rating_stats()

    modeladmin.message_user(
        request,
        f"{queryset.count()} rating(s) recalculated.",
        messages.SUCCESS,
    )


# ==========================================================
# Reset Views
# ==========================================================


@admin.action(description="Reset views")
def reset_product_views(modeladmin, request, queryset):

    updated = queryset.update(
        views=0,
    )

    modeladmin.message_user(
        request,
        f"{updated} product(s) updated.",
        messages.SUCCESS,
    )


# ==========================================================
# Reset Selling Counter
# ==========================================================


@admin.action(description="Reset selling counter")
def reset_product_sales(modeladmin, request, queryset):

    updated = queryset.update(
        selling_count=0,
    )

    modeladmin.message_user(
        request,
        f"{updated} product(s) updated.",
        messages.SUCCESS,
    )


@admin.action(description="Activate selected discount codes")
def activate_discount_codes(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"{updated} discount code(s) activated.")


@admin.action(description="Deactivate selected discount codes")
def deactivate_discount_codes(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"{updated} discount code(s) deactivated.")
