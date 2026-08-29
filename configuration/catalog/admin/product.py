"""
catalog/admin/product.py
"""

from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin

from catalog.models import Product
from django.utils.html import format_html


from .actions import (
    enable_products,
    disable_products,
    mark_products_sold_out,
    mark_products_discontinued,
    duplicate_products,
    regenerate_product_slugs,
    recalculate_product_ratings,
    reset_product_views,
    reset_product_sales,
)

from .filters import (
    DiscountFilter,
    RatingFilter,
    StockFilter,
    SoftDeleteFilter,
    HasImageFilter,
)

from .inlines import (
    RAMInline,
    CPUInline,
    GPUInline,
    HardDriveInline,
    MouseInline,
    KeyboardInline,
)


@admin.register(Product)
class ProductAdmin(ModelAdmin):

    # -----------------------------------------------------
    # General
    # -----------------------------------------------------

    compressed_fields = True

    warn_unsaved_form = True

    list_fullwidth = True

    list_per_page = 30

    ordering = ("-created",)

    save_on_top = True

    autocomplete_fields = (
        "user",
        "category",
    )

    list_select_related = (
        "user",
        "category",
    )

    search_fields = (
        "name",
        "slug",
        "description",
        "user__username",
        "category__name",
    )

    # -----------------------------------------------------
    # Filters
    # -----------------------------------------------------

    list_filter = (
        "status",
        DiscountFilter,
        RatingFilter,
        StockFilter,
        HasImageFilter,
        SoftDeleteFilter,
        "category",
        "created",
        "modified",
    )

    # -----------------------------------------------------
    # List
    # -----------------------------------------------------

    list_display = (
        "thumbnail",
        "name",
        "seller",
        "category_name",
        "status_badge",
        "price_column",
        "discount_column",
        "final_price_column",
        "stock_column",
        "rating_column",
        "comments_column",
        "views",
        "selling_count",
        "created",
    )

    list_display_links = (
        "thumbnail",
        "name",
    )

    # -----------------------------------------------------
    # Readonly
    # -----------------------------------------------------

    readonly_fields = (
        "thumbnail_large",
        "slug",
        "views",
        "selling_count",
        "average_rating",
        "rating_count",
        "price_display",
        "final_price_display",
        "discount_percentage_display",
        "created",
        "modified",
    )

    # -----------------------------------------------------
    # Fieldsets
    # -----------------------------------------------------

    fieldsets = (
        (
            _("General"),
            {
                "fields": (
                    "thumbnail_large",
                    "image",
                    "name",
                    "slug",
                    "description",
                )
            },
        ),
        (
            _("Relations"),
            {
                "fields": (
                    "user",
                    "category",
                )
            },
        ),
        (
            _("Pricing"),
            {
                "fields": (
                    "price",
                    "price_display",
                    "discount_percentage",
                    "discount_percentage_display",
                    "final_price_display",
                )
            },
        ),
        (
            _("Inventory"),
            {
                "fields": (
                    "stock",
                    "status",
                )
            },
        ),
        (
            _("Statistics"),
            {
                "classes": ("tab",),
                "fields": (
                    "views",
                    "selling_count",
                    "average_rating",
                    "rating_count",
                ),
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

    # -----------------------------------------------------
    # Inlines
    # -----------------------------------------------------

    inlines = (
        RAMInline,
        CPUInline,
        GPUInline,
        HardDriveInline,
        MouseInline,
        KeyboardInline,
    )

    # -----------------------------------------------------
    # Actions
    # -----------------------------------------------------

    actions = (
        enable_products,
        disable_products,
        mark_products_sold_out,
        mark_products_discontinued,
        duplicate_products,
        regenerate_product_slugs,
        recalculate_product_ratings,
        reset_product_views,
        reset_product_sales,
    )

    # =====================================================
    # Display methods
    # (Part 2)
    # =====================================================
    # =====================================================
    # Display Methods
    # =====================================================

    @admin.display(description=_("Image"))
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:48px;height:48px;'
                'object-fit:cover;border-radius:8px;" />',
                obj.image.url,
            )

        return "—"

    @admin.display(description=_("Preview"))
    def thumbnail_large(self, obj):
        if not obj.pk:
            return "Save object first."

        if obj.image:
            return format_html(
                '<img src="{}" style="width:220px;' 'border-radius:12px;" />',
                obj.image.url,
            )

        return "No image"

    @admin.display(
        description=_("Seller"),
        ordering="user__username",
    )
    def seller(self, obj):
        return obj.user

    @admin.display(
        description=_("Category"),
        ordering="category__name",
    )
    def category_name(self, obj):
        if obj.category:
            return obj.category.full_path

        return "—"

    @admin.display(
        description=_("Status"),
        ordering="status",
    )
    def status_badge(self, obj):

        colors = {
            Product.Status.ENABLED: "#22c55e",
            Product.Status.DISABLED: "#ef4444",
            Product.Status.SOLD_OUT: "#f59e0b",
            Product.Status.DISCONTINUED: "#6b7280",
        }

        color = colors.get(obj.status, "#6b7280")

        return format_html(
            """
            <span style="
                background:{};
                color:white;
                padding:4px 10px;
                border-radius:999px;
                font-size:12px;
                font-weight:600;">
                {}
            </span>
            """,
            color,
            obj.get_status_display(),
        )

    @admin.display(
        description=_("Price"),
        ordering="price",
    )
    def price_column(self, obj):
        return obj.price_display

    @admin.display(
        description=_("Discount"),
        ordering="discount_percentage",
    )
    def discount_column(self, obj):

        if obj.discount_percentage == 0:
            return "—"

        return format_html(
            '<span style="color:#dc2626;font-weight:bold;">{}%</span>',
            int(obj.discount_percentage),
        )

    @admin.display(
        description=_("Final Price"),
    )
    def final_price_column(self, obj):
        return obj.final_price_display

    @admin.display(
        description=_("Stock"),
        ordering="stock",
    )
    def stock_column(self, obj):

        if obj.stock == 0:
            color = "#ef4444"

        elif obj.stock < 10:
            color = "#f59e0b"

        else:
            color = "#22c55e"

        return format_html(
            """
            <span style="
                color:{};
                font-weight:bold;">
                {}
            </span>
            """,
            color,
            obj.stock,
        )

    @admin.display(
        description=_("Available"),
    )
    def available_column(self, obj):

        if obj.is_available():
            return format_html('<span style="color:#22c55e;">● Available</span>')

        return format_html('<span style="color:#ef4444;">● Unavailable</span>')

    @admin.display(
        description=_("Rating"),
        ordering="average_rating",
    )
    def rating_column(self, obj):
        rating = float(obj.average_rating or 0)

        full = int(rating)
        stars = "★" * full + "☆" * (5 - full)

        return format_html(
            '<span style="color:#f59e0b;">{}</span> {}',
            stars,
            f"{rating:.1f}",
        )

    @admin.display(
        description=_("Comments"),
        ordering="comments_total",
    )
    def comments_column(self, obj):
        return getattr(obj, "comments_total", obj.comments.count())

    @admin.display(description=_("Panel"))
    def panel_link(self, obj):

        return format_html(
            '<a class="button" href="{}" target="_blank">' "Open" "</a>",
            obj.panel_url,
        )

    @admin.display(description=_("Website"))
    def website_link(self, obj):

        return format_html(
            '<a class="button" href="{}" target="_blank">' "View" "</a>",
            obj.absolute_url,
        )

    # =====================================================
    # Queryset
    # =====================================================

    def get_queryset(self, request):
        """
        Optimized queryset for the changelist.
        """
        return (
            super()
            .get_queryset(request)
            .select_related(
                "user",
                "category",
            )
            .annotate(
                comments_total=Count("comments"),
            )
        )

    # =====================================================
    # Search
    # =====================================================

    def get_search_results(self, request, queryset, search_term):
        """
        Keep Django's default search while allowing future
        customization.
        """
        queryset, use_distinct = super().get_search_results(
            request,
            queryset,
            search_term,
        )

        return queryset, use_distinct

    # =====================================================
    # Save
    # =====================================================

    def save_model(self, request, obj, form, change):
        """
        Automatically assign the current admin user as seller
        if none has been selected.
        """

        if not obj.user_id:
            obj.user = request.user

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
        """
        Soft delete every selected object.
        """

        for obj in queryset:
            obj.delete()

    # =====================================================
    # Readonly
    # =====================================================

    def get_readonly_fields(self, request, obj=None):

        readonly = list(self.readonly_fields)

        if obj:
            readonly.append("slug")

        return readonly

    # =====================================================
    # Fieldsets
    # =====================================================

    def get_fieldsets(self, request, obj=None):
        """
        Hide statistics before the product exists.
        """

        fieldsets = list(super().get_fieldsets(request, obj))

        if obj is None:
            fieldsets = [fs for fs in fieldsets if fs[0] != _("Statistics")]

        return fieldsets

    # =====================================================
    # Inlines
    # =====================================================

    def get_inline_instances(self, request, obj=None):

        if obj is None:
            return []

        return super().get_inline_instances(
            request,
            obj,
        )

    # =====================================================
    # Permissions
    # =====================================================

    def has_view_permission(self, request, obj=None):
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj)

    # =====================================================
    # Save Related
    # =====================================================

    def save_related(self, request, form, formsets, change):

        super().save_related(
            request,
            form,
            formsets,
            change,
        )

        product = form.instance
        product.update_rating_stats()
