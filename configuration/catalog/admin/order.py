"""
catalog/admin/order.py
"""

from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin

from catalog.models import Order


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True
    save_on_top = True

    list_per_page = 40

    ordering = ("-created",)

    search_fields = (
        "order_id",
        "user__username",
        "user__email",
        "shipping_address",
        "billing_address",
        "payment__payment_id",
        "payment__transaction_id",
    )

    autocomplete_fields = (
        "user",
        "off_code",
    )

    list_select_related = (
        "user",
        "off_code",
        "payment",
    )

    list_filter = (
        "status",
        "currency",
        "created",
        "modified",
        "shipped_at",
        "delivered_at",
        "cancelled_at",
    )

    list_display = (
        "order_id",
        "customer",
        "status_badge",
        "items_count",
        "subtotal_column",
        "discount_column",
        "final_amount_column",
        "coupon_column",
        "payment_column",
        "created",
    )

    list_display_links = (
        "order_id",
        "customer",
    )

    readonly_fields = (
        "order_id",
        "subtotal_amount",
        "coupon_discount_amount",
        "final_amount",
        "created",
        "modified",
        "items_preview",
    )

    fieldsets = (
        (
            _("General"),
            {
                "fields": (
                    "order_id",
                    "user",
                    "status",
                    "currency",
                )
            },
        ),
        (
            _("Amounts"),
            {
                "fields": (
                    "subtotal_amount",
                    "coupon_discount_amount",
                    "final_amount",
                    "off_code",
                )
            },
        ),
        (
            _("Items"),
            {"fields": ("items_preview",)},
        ),
        (
            _("Addresses"),
            {
                "fields": (
                    "shipping_address",
                    "billing_address",
                )
            },
        ),
        (
            _("Fulfilment"),
            {
                "fields": (
                    "shipped_at",
                    "delivered_at",
                    "cancelled_at",
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
                "user",
                "off_code",
                "payment",
            )
            .prefetch_related("items__product")
            .annotate(
                items_total=Count("items"),
            )
        )

    # =====================================================
    # Display
    # =====================================================

    @admin.display(ordering="user__username", description=_("Customer"))
    def customer(self, obj):
        return obj.user

    @admin.display(ordering="status", description=_("Status"))
    def status_badge(self, obj):

        colors = {
            Order.Status.PENDING_PAYMENT: "#f59e0b",
            Order.Status.PAID: "#22c55e",
            Order.Status.PROCESSING: "#3b82f6",
            Order.Status.SHIPPED: "#06b6d4",
            Order.Status.DELIVERED: "#16a34a",
            Order.Status.CANCELLED: "#ef4444",
            Order.Status.REFUNDED: "#7c3aed",
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

    @admin.display(description=_("Items"))
    def items_count(self, obj):
        return obj.items_total

    @admin.display(description=_("Subtotal"))
    def subtotal_column(self, obj):
        return obj.subtotal_amount_display

    @admin.display(description=_("Discount"))
    def discount_column(self, obj):
        return obj.coupon_discount_amount

    @admin.display(description=_("Final"))
    def final_amount_column(self, obj):
        return obj.final_amount_display

    @admin.display(description=_("Coupon"))
    def coupon_column(self, obj):
        if obj.off_code:
            return obj.off_code.code
        return "—"

    @admin.display(description=_("Payment"))
    def payment_column(self, obj):
        if hasattr(obj, "payment"):
            return obj.payment.get_status_display()
        return "No Payment"

    @admin.display(description=_("Order Items"))
    def items_preview(self, obj):

        if not obj.pk:
            return "-"

        html = "<ul style='margin:0;padding-left:18px;'>"

        for item in obj.items.select_related("product"):

            name = item.product.name if item.product else "Deleted Product"

            html += (
                f"<li>{item.quantity} × " f"{name} " f"({item.subtotal_display})</li>"
            )

        html += "</ul>"

        return format_html(html)

    # =====================================================
    # Save
    # =====================================================

    def save_model(self, request, obj, form, change):
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
