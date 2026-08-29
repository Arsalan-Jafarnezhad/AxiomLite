"""Shared ID generation helpers, built entirely on the stdlib ``uuid`` module."""

import uuid


def generate_public_id() -> str:
    """Opaque identifier safe to expose in URLs/API responses (no dashes)."""
    return uuid.uuid4().hex


def generate_slug() -> str:
    """Dash-grouped unique token, handy for generated filenames."""
    return str(uuid.uuid4())
