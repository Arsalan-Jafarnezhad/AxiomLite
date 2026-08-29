"""
catalog/admin/discount.py
"""

from decimal import Decimal

from django.contrib import admin
from django.db.models import Count
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin

from catalog.models import OffCode

from .actions import (
    activate_discount_codes,
    deactivate_discount_codes,
)

from .filters import (
    CouponValidityFilter,
    SoftDeleteFilter,
)


@admin.register(OffCode)
class OffCodeAdmin(ModelAdmin):

    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True
    save_on_top = True

    list_per_page = 40

    ordering = ("-created",)

    search_fields = (
        "code",
        "description",
    )

    readonly_fields = (
        "created",
        "modified",
        "usages",
        "total_discount_given_display",
        "validity_display",
    )

    list_filter = (
        CouponValidityFilter,
        SoftDeleteFilter,
        "is_active",
        "starts_at",
        "ends_at",
        "created",
    )

    list_display = (
        "code",
        "discount_display",
        "status_badge",
        "usage_display",
        "budget_display",
        "orders_display",
        "validity_display",
        "created",
    )

    fieldsets = (
        (
            _("General"),
            {
                "fields": (
                    "code",
                    "description",
                    "is_active",
                )
            },
        ),
        (
            _("Validity"),
            {
                "fields": (
                    "starts_at",
                    "ends_at",
                    "validity_display",
                )
            },
        ),
        (
            _("Discount"),
            {
                "fields": (
                    "discount_percent",
                    "fixed_discount_amount",
                    "max_discount_per_use",
                )
            },
        ),
        (
            _("Limits"),
            {
                "fields": (
                    "minimum_order_amount",
                    "usage_limit",
                    "usage_limit_per_user",
                    "total_discount_capacity",
                )
            },
        ),
        (
            _("Statistics"),
            {
                "fields": (
                    "usages",
                    "total_discount_given_display",
                )
            },
        ),
        (
            _("Dates"),
            {
                "classes": ("collapse",),
                "fields": (
                    "created",
                    "modified",
                ),
            },
        ),
    )

    actions = (
        activate_discount_codes,
        deactivate_discount_codes,
    )

    # =====================================================
    # Queryset
    # =====================================================

    def get_queryset(self, request):

        return (
            super()
            .get_queryset(request)
            .annotate(
                order_count=Count("orders"),
            )
        )

    # =====================================================
    # Display
    # =====================================================

    @admin.display(description=_("Discount"))
    def discount_display(self, obj):

        if obj.discount_percent is not None:
            return format_html(
                "<strong>{}%</strong>",
                obj.discount_percent,
            )

        if obj.fixed_discount_amount:
            return obj.fixed_discount_amount

        return "—"

    @admin.display(
        description=_("Status"),
        ordering="is_active",
    )
    def status_badge(self, obj):

        if not obj.is_active:

            return format_html('<span style="color:#ef4444;">● Inactive</span>')

        if obj.is_expired_by_time:

            return format_html('<span style="color:#dc2626;">● Expired</span>')

        if obj.is_expired_by_total_uses:

            return format_html('<span style="color:#ea580c;">● Usage Limit</span>')

        if obj.is_expired_by_total_discount_cap:

            return format_html('<span style="color:#ea580c;">● Budget Limit</span>')

        return format_html('<span style="color:#22c55e;">● Active</span>')

    @admin.display(description=_("Orders"))
    def orders_display(self, obj):
        return obj.order_count

    @admin.display(description=_("Usage"))
    def usage_display(self, obj):

        if obj.usage_limit:

            return f"{obj.usages} / {obj.usage_limit}"

        return obj.usages

    @admin.display(description=_("Budget"))
    def budget_display(self, obj):

        if obj.total_discount_capacity:

            return (
                f"{obj.total_discount_given} / " f"{obj.total_discount_capacity.amount}"
            )

        return "Unlimited"

    @admin.display(description=_("Total Discount"))
    def total_discount_given_display(self, obj):
        return obj.total_discount_given

    @admin.display(description=_("Validity"))
    def validity_display(self, obj):

        if obj.is_valid:
            return format_html('<span style="color:#22c55e;">Valid</span>')

        return format_html('<span style="color:#ef4444;">Invalid</span>')

    # =====================================================
    # Save
    # =====================================================

    def save_model(self, request, obj, form, change):

        if obj.discount_percent is not None and obj.fixed_discount_amount:
            raise ValueError("Only one discount type can be used.")

        super().save_model(
            request,
            obj,
            form,
            change,
        )

    # =====================================================
    # Delete
    # =====================================================

    def delete_queryset(self, request, queryset):

        for obj in queryset:
            obj.delete()
