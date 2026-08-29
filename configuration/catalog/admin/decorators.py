"""
catalog/admin/decorators.py

Reusable display decorators and helpers for Django Unfold admin.

These helpers reduce repetitive code for:

- @admin.display(...)
- Colored badges
- Boolean badges
- Money formatting
- Ratings
- Status chips
- Image thumbnails
"""

from __future__ import annotations

from functools import wraps

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import SafeString

# ------------------------------------------------------------------------------
# admin.display shortcut
# ------------------------------------------------------------------------------


def display(**kwargs):
    """
    Shortcut around admin.display.

    Example:

        @display(description="Price", ordering="price")
        def price_display(...):
            ...
    """
    return admin.display(**kwargs)


# ------------------------------------------------------------------------------
# Generic badge
# ------------------------------------------------------------------------------


def badge(
    color: str,
    *,
    empty: str = "—",
    suffix: str = "",
):
    """
    Wrap a value inside a colored Unfold badge.

    Example:

        @badge("success")
        def stock(...):
            return obj.stock
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = func(*args, **kwargs)

            if value in (None, ""):
                value = empty

            return format_html(
                """
                <span class="inline-flex rounded-md px-2 py-1 text-xs font-semibold
                             bg-{}-100 text-{}-700 dark:bg-{}-900 dark:text-{}-300">
                    {}{}
                </span>
                """,
                color,
                color,
                color,
                color,
                value,
                suffix,
            )

        return wrapper

    return decorator


# ------------------------------------------------------------------------------
# Predefined colors
# ------------------------------------------------------------------------------

success_badge = badge("green")
warning_badge = badge("yellow")
danger_badge = badge("red")
info_badge = badge("blue")
gray_badge = badge("gray")


# ------------------------------------------------------------------------------
# Boolean badge
# ------------------------------------------------------------------------------


def boolean_badge(true_text="Yes", false_text="No"):
    """
    Display booleans as colored badges.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            if func(*args, **kwargs):
                return format_html(
                    '<span class="text-green-600 font-semibold">✓ {}</span>',
                    true_text,
                )

            return format_html(
                '<span class="text-red-600 font-semibold">✕ {}</span>',
                false_text,
            )

        return wrapper

    return decorator


# ------------------------------------------------------------------------------
# Rating stars
# ------------------------------------------------------------------------------


def stars(maximum=5):
    """
    Render numeric rating as stars.

    Example

        4.5

        ★★★★☆
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            rating = float(func(*args, **kwargs) or 0)

            full = int(rating)

            empty = maximum - full

            return SafeString(
                '<span style="color:#f59e0b">'
                + "★" * full
                + "</span>"
                + '<span style="color:#d1d5db">'
                + "☆" * empty
                + "</span>"
                + f" {rating:.1f}"
            )

        return wrapper

    return decorator


# ------------------------------------------------------------------------------
# Money
# ------------------------------------------------------------------------------


def money():
    """
    Formats Money objects.

    Uses model's amount_display property when available.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            value = func(*args, **kwargs)

            if value is None:
                return "—"

            return str(value)

        return wrapper

    return decorator


# ------------------------------------------------------------------------------
# Image preview
# ------------------------------------------------------------------------------


def image_preview(width=60):
    """
    Render ImageField as thumbnail.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            image = func(*args, **kwargs)

            if not image:
                return "—"

            return format_html(
                '<img src="{}" '
                'style="width:{}px;height:{}px;'
                'border-radius:8px;object-fit:cover;" />',
                image.url,
                width,
                width,
            )

        return wrapper

    return decorator


# ------------------------------------------------------------------------------
# Colored status
# ------------------------------------------------------------------------------

STATUS_COLORS = {
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "info": "blue",
}


def status_badge(color_attr="status_class"):
    """
    Uses model.status_class

    Example

        Product.status_class

            success
            warning
            error
            info
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            obj = args[1]

            color = STATUS_COLORS.get(
                getattr(obj, color_attr, "gray"),
                "gray",
            )

            value = func(*args, **kwargs)

            return format_html(
                """
                <span class="inline-flex rounded-md px-2 py-1 text-xs font-semibold
                    bg-{}-100 text-{}-700
                    dark:bg-{}-900 dark:text-{}-300">
                    {}
                </span>
                """,
                color,
                color,
                color,
                color,
                value,
            )

        return wrapper

    return decorator


@display(description="Status", ordering="status")
@status_badge()
def status_display(self, obj):
    return obj.get_status_display()


@display(description="Rating")
@stars()
def rating(self, obj):
    return obj.average_rating


@display(description="Image")
@image_preview(70)
def thumbnail(self, obj):
    return obj.image


@display(description="Stock")
@success_badge
def stock_badge(self, obj):
    return obj.stock
