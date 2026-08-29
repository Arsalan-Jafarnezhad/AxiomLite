"""Upload-path builders for FileField/ImageField ``upload_to`` callables."""

from mimetypes import guess_extension, guess_type

from .ids import generate_slug


def safe_extension(filename: str) -> str:
    """Guesses a safe file extension from *filename*, falling back to .jpg."""
    guessed = guess_extension(guess_type(filename)[0] or "")
    return guessed or ".jpg"


def profile_image_upload_path(instance, filename: str) -> str:
    return (
        f"accounts/profiles/{instance.user.public_id}/"
        f"{generate_slug()}{safe_extension(filename)}"
    )


def rank_image_upload_path(instance, filename: str) -> str:
    return f"accounts/ranks/{generate_slug()}{safe_extension(filename)}"
