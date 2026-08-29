"""
shop/formatting.py

Pure display helpers — no ORM, no models, trivially unit-testable.
"""

from __future__ import annotations

from typing import Any

from moneyed import Money  # transitive dep of django-money


def format_money(amount: Money) -> str:
    """
    Returns a human-readable money string using the currency's own symbol/code.

    Examples:
        ``1,250,000 IRT``  →  ``1,250,000 T``   (overridden below for IRT)
        ``€1,250.00``
    """
    # Special-case Iranian Toman: drop decimal places, add "T" suffix.
    if str(amount.currency) in {"IRT", "IRR"}:
        return f"{amount.amount:,.0f} {'T' if str(amount.currency) == 'IRT' else 'R'}"
    return f"{amount.currency.symbol}{amount.amount:,.2f}"


def format_price(amount: Any, currency: str = "IRT") -> str:
    """
    Convenience wrapper when you have a raw number rather than a ``Money`` obj.
    """
    if str(currency) in {"IRT", "IRR"}:
        suffix = "T" if currency == "IRT" else "R"
        return f"{amount:,.0f} {suffix}"
    return f"{currency} {amount:,.2f}"


def get_polarity_color_class(polarity: float) -> str:
    """Maps a 0–100 polarity score to a CSS severity token."""
    if polarity >= 80:
        return "success"
    if polarity >= 60:
        return "info"
    if polarity >= 40:
        return "warning"
    return "error"
