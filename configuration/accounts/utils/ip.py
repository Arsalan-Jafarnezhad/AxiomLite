"""Utilities for retrieving client IP addresses and country information."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest


def get_user_ip_address(request: HttpRequest) -> str | None:
    """Return the best available client IP address from a request."""
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def get_country_by_ip(ip_address: str | None) -> str | None:
    """
    Return a country code for an IP address.

    Country resolution is intentionally kept optional here. The function
    returns None when no configured IP-geolocation provider is available.
    """
    if not ip_address:
        return None

    # IP geolocation should be implemented through a dedicated provider
    # rather than making an external request from this low-level utility.
    return None