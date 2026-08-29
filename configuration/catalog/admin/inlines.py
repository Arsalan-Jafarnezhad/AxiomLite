"""
catalog/admin/inlines.py
"""

from django.contrib import admin

from catalog.models import (
    RAM,
    CPU,
    GPU,
    HardDrive,
    Mouse,
    Keyboard,
)

# =============================================================================
# Base Inline
# =============================================================================


class BaseSpecInline(admin.StackedInline):
    """
    Base inline for all hardware specification models.
    """

    extra = 0
    max_num = 1
    can_delete = True
    show_change_link = True

    classes = ("tab",)


# =============================================================================
# RAM
# =============================================================================


class RAMInline(BaseSpecInline):
    model = RAM

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "capacity_gb",
                    "speed_mhz",
                    "ddr_type",
                )
            },
        ),
    )


# =============================================================================
# CPU
# =============================================================================


class CPUInline(BaseSpecInline):
    model = CPU

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("cores", "threads"),
                    ("base_clock", "boost_clock"),
                    ("socket", "tdp_watts"),
                )
            },
        ),
    )


# =============================================================================
# GPU
# =============================================================================


class GPUInline(BaseSpecInline):
    model = GPU

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("memory_gb", "memory_type"),
                    ("core_clock_mhz", "boost_clock_mhz"),
                    "tdp_watts",
                )
            },
        ),
    )


# =============================================================================
# Hard Drive
# =============================================================================


class HardDriveInline(BaseSpecInline):
    model = HardDrive

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("capacity_gb", "drive_type"),
                    ("form_factor", "interface"),
                    ("read_speed_mb_s", "write_speed_mb_s"),
                )
            },
        ),
    )


# =============================================================================
# Mouse
# =============================================================================


class MouseInline(BaseSpecInline):
    model = Mouse

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("connection_type", "dpi"),
                    ("buttons_count", "weight_grams"),
                    ("is_gaming", "has_rgb"),
                )
            },
        ),
    )


# =============================================================================
# Keyboard
# =============================================================================


class KeyboardInline(BaseSpecInline):
    model = Keyboard

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("layout", "switch_type"),
                    ("is_gaming", "has_rgb"),
                    ("has_num_pad", "is_wireless"),
                )
            },
        ),
    )
