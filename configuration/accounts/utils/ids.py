"""Utilities for generating public identifiers and slugs."""

import secrets
import string

from django.utils.text import slugify


PUBLIC_ID_ALPHABET = string.ascii_letters + string.digits
PUBLIC_ID_LENGTH = 16


def generate_public_id(length: int = PUBLIC_ID_LENGTH) -> str:
    """Generate a cryptographically secure public identifier."""
    return "".join(
        secrets.choice(PUBLIC_ID_ALPHABET)
        for _ in range(length)
    )


def generate_slug(value: str) -> str:
    """Generate a normalized URL-friendly slug."""
    return slugify(value.strip())