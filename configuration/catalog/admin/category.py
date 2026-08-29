from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from unfold.admin import ModelAdmin

from catalog.models import Category


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """
    Unfold admin for Category.
    """

    # -----------------------------
    # General
    # -----------------------------

    compressed_fields = True
    warn_unsaved_form = True

    ordering = ("name",)

    search_fields = (
        "name",
        "slug",
        "parent__name",
    )

    autocomplete_fields = ("parent",)

    list_per_page = 30

    # -----------------------------
    # List
    # -----------------------------

    list_display = (
        "tree_name",
        "parent",
        "products_count",
        "children_count",
        "slug",
        "created",
    )

    list_display_links = ("tree_name",)

    list_filter = (
        "created",
        "modified",
    )

    list_select_related = ("parent",)

    # -----------------------------
    # Readonly
    # -----------------------------

    readonly_fields = (
        "slug",
        "created",
        "modified",
        "products_count_display",
        "children_count_display",
        "full_path_display",
    )

    # -----------------------------
    # Fieldsets
    # -----------------------------

    fieldsets = (
        (
            "Category",
            {
                "fields": (
                    "name",
                    "parent",
                    "slug",
                ),
            },
        ),
        (
            "Information",
            {
                "classes": ("tab",),
                "fields": (
                    "full_path_display",
                    "products_count_display",
                    "children_count_display",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": (
                    "created",
                    "modified",
                ),
            },
        ),
    )

    # -----------------------------
    # Actions
    # -----------------------------

    actions = ("clear_parent",)

    @admin.action(description="Remove selected categories from parent")
    def clear_parent(self, request, queryset):
        queryset.update(parent=None)

    # -----------------------------
    # Query Optimization
    # -----------------------------

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("parent")
            .annotate(
                product_total=Count("products", distinct=True),
                child_total=Count("children", distinct=True),
            )
        )

    # -----------------------------
    # Display Methods
    # -----------------------------

    @admin.display(
        description="Category",
        ordering="name",
    )
    def tree_name(self, obj):
        depth = 0
        node = obj.parent

        while node:
            depth += 1
            node = node.parent

        return format_html(
            "{}{}",
            "&nbsp;" * depth * 6,
            obj.name,
        )

    @admin.display(
        description="Products",
        ordering="product_total",
    )
    def products_count(self, obj):
        color = "green" if obj.product_total else "gray"

        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.product_total,
        )

    @admin.display(
        description="Children",
        ordering="child_total",
    )
    def children_count(self, obj):
        color = "blue" if obj.child_total else "gray"

        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.child_total,
        )

    # -----------------------------
    # Readonly Helpers
    # -----------------------------

    @admin.display(description="Full Path")
    def full_path_display(self, obj):
        return obj.full_path

    @admin.display(description="Products")
    def products_count_display(self, obj):
        return obj.products.count()

    @admin.display(description="Sub Categories")
    def children_count_display(self, obj):
        return obj.children.count()
