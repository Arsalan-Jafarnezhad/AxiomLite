"""
catalog/file_utils.py

Upload-path helpers for ImageField / FileField.
Keep these separate so models stay readable and the logic is unit-testable
without needing a full Django model instance.
"""
from mimetypes import guess_extension, guess_type

from catalog.utils.id import generate_key, _format_id


def _safe_extension(filename: str) -> str:
    mime, _ = guess_type(filename)
    return guess_extension(mime or "") or ".jpg"


def get_product_image_path(instance, filename):
    ext = _safe_extension(filename)

    user_segment = _format_id(instance.user_id)

    # Product doesn't have a PK on first save.
    product_segment = (
        _format_id(instance.pk)
        if instance.pk
        else generate_key()
    )

    return (
        f"catalog/products/"
        f"{user_segment}/"
        f"{product_segment}/"
        f"{generate_key()}{ext}"
    )