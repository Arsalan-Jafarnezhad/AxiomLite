"""
catalog/id_utils.py

All UUID-v7-based identifier helpers live here.
Nothing in this module imports from Django, so it stays fast and testable.
"""
from uuid import uuid7


def _raw_id() -> str:
    return uuid7().hex


def _format_id(value) -> str:
    """
    Formats any value into xxxx-xxxx-xxxx style.

    Accepts:
        UUID
        int
        str
        None
    """
    if value is None:
        return generate_key()

    raw = str(value).replace("-", "")

    return "-".join(
        raw[i:i + 4]
        for i in range(0, len(raw), 4)
    )


def generate_key() -> str:
    return _format_id(_raw_id())


generate_slug = generate_key