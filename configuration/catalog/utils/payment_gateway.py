"""
shop/payment_gateway.py

Payment gateway integration.

Routing logic
─────────────
- IRT / IRR  →  Zarinpal
- Everything else  →  ``shop:payment-internal`` (internal HTML payment page)

All network I/O is isolated here so views and models stay testable with mocks.
"""

from __future__ import annotations

import json
from typing import Any

from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse
from httpx import ConnectError, TimeoutException, post

from catalog.constants import (
    is_zarinpal_currency,
    zarinpal_request_url,
    zarinpal_start_pay_url,
    zarinpal_verify_url,
)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _headers(payload: str) -> dict[str, str]:
    return {
        "content-type": "application/json",
        "content-length": str(len(payload)),
        "accept": "application/json",
    }


def _post(url: str, data: dict[str, Any], timeout: int = 10):
    payload = json.dumps(data)
    try:
        return post(url, data=payload, headers=_headers(payload), timeout=timeout)
    except TimeoutException:
        return None
    except ConnectError:
        return None


# ── Currency router ───────────────────────────────────────────────────────────

class PaymentRoute:
    """
    Describes where a payment should be directed.

    Attributes:
        use_zarinpal:   ``True``  → redirect to Zarinpal gateway.
        use_internal:   ``True``  → render internal payment template.
        redirect_url:   Ready-to-use URL string (set after gateway request).
    """

    def __init__(self, *, use_zarinpal: bool, redirect_url: str = "") -> None:
        self.use_zarinpal = use_zarinpal
        self.use_internal = not use_zarinpal
        self.redirect_url = redirect_url

    def __repr__(self) -> str:
        label = "Zarinpal" if self.use_zarinpal else "Internal"
        return f"<PaymentRoute: {label}>"


def resolve_payment_route(currency_code: str, payment_id: str) -> PaymentRoute:
    """
    Determines where to direct the user for payment based on currency.

    Args:
        currency_code:  ISO 4217 currency code (e.g. ``"IRT"``, ``"USD"``).
        payment_id:     Internal payment ID (used to build the internal URL).

    Returns:
        :class:`PaymentRoute` with the appropriate flags set.
        *Does not* perform the Zarinpal request — call :func:`payment_request`
        separately when ``route.use_zarinpal`` is ``True``.
    """
    if is_zarinpal_currency(currency_code):
        return PaymentRoute(use_zarinpal=True)
    internal_url = reverse("shop:payment-internal", kwargs={"payment_id": payment_id})
    return PaymentRoute(use_zarinpal=False, redirect_url=internal_url)


# ── Zarinpal ──────────────────────────────────────────────────────────────────

def payment_request(
    amount: float,
    description: str,
    callback_url: str,
    request: HttpRequest,
) -> dict[str, Any]:
    """
    Initiates a Zarinpal payment request.

    Returns on success::

        {
            "ok": True,
            "authority": "<authority>",
            "redirect_url": "<start-pay URL>",
        }

    Returns on failure::

        {"ok": False, "error": "<reason>"}

    **Only call this when** ``resolve_payment_route().use_zarinpal`` **is** ``True``.
    """
    data = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "amount": float(amount),
        "description": description,
        "callback_url": callback_url,
        "currency": "IRT",
        "metadata": {
            "mobile": getattr(request.user, "phone_number", ""),
            "email": getattr(request.user, "email", ""),
        },
    }
    resp = _post(zarinpal_request_url(), data)
    if resp is None:
        return {"ok": False, "error": "Connection failure"}
    if resp.status_code != 200:
        return {"ok": False, "error": f"HTTP {resp.status_code}", "raw": resp.text}

    body = resp.json()
    code = body.get("data", {}).get("code")
    if code == 100:
        authority = body["data"]["authority"]
        return {
            "ok": True,
            "authority": authority,
            "redirect_url": f"{zarinpal_start_pay_url()}{authority}",
            "raw": body,
        }
    return {"ok": False, "error": f"Gateway code {code}", "raw": body}


def payment_verify(amount: float, authority: str) -> dict[str, Any]:
    """
    Verifies a completed Zarinpal payment.

    Returns on success::

        {
            "ok": True,
            "is_verified": True,
            "already_verified": False,
            "transaction_id": "<ref_id>",
        }
    """
    data = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "amount": float(amount),
        "authority": authority,
    }
    resp = _post(zarinpal_verify_url(), data)
    if resp is None:
        return {"ok": False, "error": "Connection failure"}
    if resp.status_code != 200:
        return {"ok": False, "error": f"HTTP {resp.status_code}"}

    body = resp.json()
    code = body.get("data", {}).get("code")
    result: dict[str, Any] = {"ok": True, "raw": body}

    match code:
        case 100:
            result |= {"is_verified": True, "already_verified": False,
                       "transaction_id": body["data"]["ref_id"]}
        case 101:
            result |= {"is_verified": True, "already_verified": True,
                       "transaction_id": body["data"]["ref_id"]}
        case _:
            result |= {"is_verified": False, "already_verified": False,
                       "error": f"Gateway code {code}"}
    return result
