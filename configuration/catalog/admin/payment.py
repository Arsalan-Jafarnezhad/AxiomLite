"""
catalog/admin/payment.py
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin

from catalog.models import Payment

from .filters import (
    PaymentStatusFilter,
    SoftDeleteFilter,
)


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True
    save_on_top = True

    list_per_page = 40

    ordering = ("-created",)

    search_fields = (
        "payment_id",
        "transaction_id",
        "authority",
        "order__order_id",
        "order__user__username",
        "order__user__email",
        "user_ip_address",
    )

    autocomplete_fields = ("order",)

    list_select_related = (
        "order",
        "order__user",
    )

    list_filter = (
        PaymentStatusFilter,
        SoftDeleteFilter,
        "payment_method",
        "created",
        "paid_at",
        "failed_at",
        "cancelled_at",
        "refunded_at",
    )

    list_display = (
        "payment_id",
        "order_column",
        "customer_column",
        "status_badge",
        "method_badge",
        "amount_column",
        "vat_column",
        "transaction_column",
        "created",
    )

    list_display_links = (
        "payment_id",
        "order_column",
    )

    readonly_fields = (
        "payment_id",
        "transaction_id",
        "authority",
        "amount_display",
        "vat_amount_display",
        "gateway_response",
        "user_ip_address",
        "payment_request_time",
        "paid_at",
        "failed_at",
        "cancelled_at",
        "refunded_at",
        "created",
        "modified",
    )

    fieldsets = (
        (
            _("General"),
            {
                "fields": (
                    "order",
                    "payment_id",
                    "status",
                    "payment_method",
                )
            },
        ),
        (
            _("Financial"),
            {
                "fields": (
                    "amount",
                    "amount_display",
                    "value_added_tax",
                    "vat_amount_display",
                )
            },
        ),
        (
            _("Gateway"),
            {
                "fields": (
                    "transaction_id",
                    "authority",
                    "gateway_response",
                    "user_ip_address",
                )
            },
        ),
        (
            _("Timeline"),
            {
                "fields": (
                    "payment_request_time",
                    "paid_at",
                    "failed_at",
                    "cancelled_at",
                    "refunded_at",
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

    # =====================================================
    # Queryset
    # =====================================================

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "order",
                "order__user",
            )
        )

    # =====================================================
    # Display
    # =====================================================

    @admin.display(
        description=_("Order"),
        ordering="order__order_id",
    )
    def order_column(self, obj):
        return obj.order.order_id

    @admin.display(
        description=_("Customer"),
        ordering="order__user__username",
    )
    def customer_column(self, obj):
        return obj.order.user

    @admin.display(
        description=_("Amount"),
    )
    def amount_column(self, obj):
        return obj.amount_display

    @admin.display(
        description=_("VAT"),
    )
    def vat_column(self, obj):
        return obj.vat_amount_display

    @admin.display(
        description=_("Transaction"),
    )
    def transaction_column(self, obj):
        return obj.transaction_id or "—"

    @admin.display(
        description=_("Status"),
        ordering="status",
    )
    def status_badge(self, obj):

        colors = {
            Payment.Status.PENDING: "#f59e0b",
            Payment.Status.SUCCESS: "#22c55e",
            Payment.Status.FAILED: "#ef4444",
            Payment.Status.REFUNDED: "#8b5cf6",
            Payment.Status.CANCELLED: "#6b7280",
        }

        return format_html(
            """
            <span style="
                background:{};
                color:white;
                padding:4px 10px;
                border-radius:999px;
                font-weight:600;">
                {}
            </span>
            """,
            colors.get(obj.status, "#6b7280"),
            obj.get_status_display(),
        )

    @admin.display(
        description=_("Method"),
    )
    def method_badge(self, obj):

        if not obj.payment_method:
            return "—"

        return format_html(
            """
            <span style="
                background:#2563eb;
                color:white;
                padding:4px 8px;
                border-radius:999px;">
                {}
            </span>
            """,
            obj.get_payment_method_display(),
        )

    # =====================================================
    # Permissions
    # =====================================================

    def has_delete_permission(self, request, obj=None):
        """
        Prevent deleting successful payments.
        """
        if obj and obj.status == Payment.Status.SUCCESS:
            return False

        return super().has_delete_permission(
            request,
            obj,
        )

    # =====================================================
    # Readonly
    # =====================================================

    def get_readonly_fields(self, request, obj=None):

        readonly = list(self.readonly_fields)

        if obj and obj.status == Payment.Status.SUCCESS:
            readonly.extend(
                [
                    "status",
                    "payment_method",
                    "amount",
                    "value_added_tax",
                    "order",
                ]
            )

        return readonly

    # =====================================================
    # Delete
    # =====================================================

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()
