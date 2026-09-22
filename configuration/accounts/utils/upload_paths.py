"""Upload path helpers for accounts-related media."""

from pathlib import Path

from django.core.exceptions import ValidationError


ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
}


def safe_extension(filename: str) -> str:
    """Return a normalized and validated file extension."""
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            "Unsupported file extension.",
        )

    return extension


def profile_image_upload_path(instance, filename: str) -> str:
    """Return the upload path for a user's profile image."""
    extension = safe_extension(filename)

    return (
        f"accounts/profiles/"
        f"{instance.user.public_id}/"
        f"avatar{extension}"
    )


def rank_image_upload_path(instance, filename: str) -> str:
    """Return the upload path for a rank image."""
    extension = safe_extension(filename)

    return (
        f"accounts/ranks/"
        f"{instance.public_id}/"
        f"image{extension}"
    )