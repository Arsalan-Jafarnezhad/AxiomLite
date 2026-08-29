"""
catalog/admin/comment.py
"""

from django.contrib import admin
from django.db.models import Prefetch
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin

from catalog.models import ProductComment

from .filters import (
    SoftDeleteFilter,
    CommentRatingFilter,
)


@admin.register(ProductComment)
class ProductCommentAdmin(ModelAdmin):
    """
    Admin for product comments.
    """

    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True
    save_on_top = True
    list_per_page = 40

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    search_fields = (
        "text",
        "product__name",
        "product__slug",
        "user__username",
        "user__email",
    )

    autocomplete_fields = (
        "product",
        "user",
    )

    list_select_related = (
        "product",
        "user",
    )

    ordering = ("-created",)

    # -----------------------------------------------------
    # Filters
    # -----------------------------------------------------

    list_filter = (
        CommentRatingFilter,
        SoftDeleteFilter,
        "created",
        "modified",
    )

    # -----------------------------------------------------
    # List
    # -----------------------------------------------------

    list_display = (
        "product_name",
        "user_name",
        "rating_display",
        "comment_preview",
        "created",
    )

    list_display_links = (
        "product_name",
        "comment_preview",
    )

    # -----------------------------------------------------
    # Readonly
    # -----------------------------------------------------

    readonly_fields = (
        "created",
        "modified",
    )

    # -----------------------------------------------------
    # Fieldsets
    # -----------------------------------------------------

    fieldsets = (
        (
            _("Comment"),
            {
                "fields": (
                    "product",
                    "user",
                    "rating",
                    "text",
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
                "product",
                "user",
            )
        )

    # =====================================================
    # Display Methods
    # =====================================================

    @admin.display(
        description=_("Product"),
        ordering="product__name",
    )
    def product_name(self, obj):
        if obj.product:
            return obj.product.name
        return "Deleted Product"

    @admin.display(
        description=_("User"),
        ordering="user__username",
    )
    def user_name(self, obj):
        return obj.user

    @admin.display(
        description=_("Rating"),
        ordering="rating",
    )
    def rating_display(self, obj):

        if obj.rating is None:
            return "—"

        stars = "★" * obj.rating + "☆" * (5 - obj.rating)

        return format_html(
            '<span style="color:#f59e0b;">{}</span>',
            stars,
        )

    @admin.display(description=_("Comment"))
    def comment_preview(self, obj):

        text = obj.text

        if len(text) > 80:
            text = text[:80] + "..."

        return text

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

        if obj.product:
            obj.product.update_rating_stats()

    # =====================================================
    # Delete
    # =====================================================

    def delete_queryset(self, request, queryset):

        products = set(
            queryset.values_list(
                "product",
                flat=True,
            )
        )

        super().delete_queryset(
            request,
            queryset,
        )

        from catalog.models import Product

        for product in Product.objects.filter(pk__in=products):
            product.update_rating_stats()
