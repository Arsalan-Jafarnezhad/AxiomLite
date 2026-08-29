"""
shop/request_utils.py

Lightweight helpers for inspecting Django HttpRequest objects.
"""

from django.http import HttpRequest


def get_client_ip(request: HttpRequest) -> str | None:
    """
    Returns the real client IP, honouring ``X-Forwarded-For`` (set by load
    balancers / proxies) before falling back to ``REMOTE_ADDR``.
    """
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        # X-Forwarded-For can be a comma-separated list; the first IP is the client.
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def is_ajax(request: HttpRequest) -> bool:
    """Returns ``True`` if the request was made via XMLHttpRequest."""
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"
