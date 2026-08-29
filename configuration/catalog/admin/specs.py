"""
catalog/admin/specs.py
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin

from catalog.models import (
    RAM,
    CPU,
    GPU,
    HardDrive,
    Mouse,
    Keyboard,
)

# =============================================================================
# Base Admin
# =============================================================================


class BaseSpecAdmin(ModelAdmin):
    """
    Shared functionality for all hardware specification models.
    """

    compressed_fields = True
    list_fullwidth = True
    warn_unsaved_form = True
    save_on_top = True

    list_per_page = 50

    autocomplete_fields = ("product",)

    search_fields = (
        "product__name",
        "product__slug",
    )

    list_select_related = ("product",)

    ordering = ("product__name",)

    readonly_fields = (
        "created",
        "modified",
    )

    fieldsets = (
        (
            None,
            {
                "fields": ("product",),
            },
        ),
        (
            _("Metadata"),
            {
                "classes": ("collapse",),
                "fields": (
                    "created",
                    "modified",
                ),
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        """
        Automatically prepend the model specific fields
        before the metadata section.
        """
        return (
            (
                None,
                {
                    "fields": ("product", *self.spec_fields),
                },
            ),
            self.fieldsets[1],
        )


@admin.register(RAM)
class RAMAdmin(BaseSpecAdmin):

    spec_fields = (
        "capacity_gb",
        "speed_mhz",
        "ddr_type",
    )

    list_display = (
        "product",
        "capacity_gb",
        "speed_mhz",
        "ddr_type",
    )

    list_filter = (
        "ddr_type",
        "created",
    )


@admin.register(CPU)
class CPUAdmin(BaseSpecAdmin):

    spec_fields = (
        ("cores", "threads"),
        ("base_clock", "boost_clock"),
        ("socket", "tdp_watts"),
    )

    list_display = (
        "product",
        "cores",
        "threads",
        "base_clock",
        "boost_clock",
        "socket",
        "tdp_watts",
    )

    list_filter = (
        "socket",
        "created",
    )


@admin.register(GPU)
class GPUAdmin(BaseSpecAdmin):

    spec_fields = (
        ("memory_gb", "memory_type"),
        ("core_clock_mhz", "boost_clock_mhz"),
        "tdp_watts",
    )

    list_display = (
        "product",
        "memory_gb",
        "memory_type",
        "core_clock_mhz",
        "boost_clock_mhz",
        "tdp_watts",
    )

    list_filter = (
        "memory_type",
        "created",
    )


@admin.register(HardDrive)
class HardDriveAdmin(BaseSpecAdmin):

    spec_fields = (
        ("capacity_gb", "drive_type"),
        ("form_factor", "interface"),
        ("read_speed_mb_s", "write_speed_mb_s"),
    )

    list_display = (
        "product",
        "capacity_gb",
        "drive_type",
        "interface",
        "read_speed_mb_s",
        "write_speed_mb_s",
    )

    list_filter = (
        "drive_type",
        "interface",
        "created",
    )


@admin.register(Mouse)
class MouseAdmin(BaseSpecAdmin):

    spec_fields = (
        ("connection_type", "dpi"),
        ("buttons_count", "weight_grams"),
        ("is_gaming", "has_rgb"),
    )

    list_display = (
        "product",
        "connection_type",
        "dpi",
        "buttons_count",
        "weight_grams",
        "is_gaming",
        "has_rgb",
    )

    list_filter = (
        "connection_type",
        "is_gaming",
        "has_rgb",
        "created",
    )

    list_editable = (
        "is_gaming",
        "has_rgb",
    )


@admin.register(Keyboard)
class KeyboardAdmin(BaseSpecAdmin):

    spec_fields = (
        ("layout", "switch_type"),
        ("is_gaming", "has_rgb"),
        ("has_num_pad", "is_wireless"),
    )

    list_display = (
        "product",
        "layout",
        "switch_type",
        "is_wireless",
        "is_gaming",
        "has_rgb",
        "has_num_pad",
    )

    list_filter = (
        "layout",
        "switch_type",
        "is_wireless",
        "is_gaming",
        "has_rgb",
        "created",
    )

    list_editable = (
        "is_wireless",
        "is_gaming",
        "has_rgb",
    )
