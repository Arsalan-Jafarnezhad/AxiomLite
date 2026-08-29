"""
shop/constants.py

Application-wide constants.  Nothing here imports Django at module load
time — helpers that need settings use lazy functions so they are safe to
call after ``django.setup()``.
"""

from __future__ import annotations

# ── Display ───────────────────────────────────────────────────────────────────

DATETIME_DISPLAY_FORMAT = "%A / %Y - %m - %d / %I:%M:%S %p"

# ── Currency routing ──────────────────────────────────────────────────────────

#: Currencies that are routed to the Zarinpal gateway.
#: All other currencies fall through to the internal payment page.
ZARINPAL_CURRENCIES: frozenset[str] = frozenset({"IRT", "IRR"})


def is_zarinpal_currency(currency_code: str) -> bool:
    """Returns ``True`` when *currency_code* should be paid via Zarinpal."""
    return currency_code.upper() in ZARINPAL_CURRENCIES


# ── Zarinpal URLs (lazy — reads settings only when called) ────────────────────

def _zarinpal_domain() -> str:
    from django.conf import settings
    return "sandbox" if getattr(settings, "ZARINPAL_SANDBOX", False) else "payment"


def zarinpal_request_url() -> str:
    return f"https://{_zarinpal_domain()}.zarinpal.com/pg/v4/payment/request.json"


def zarinpal_start_pay_url() -> str:
    return f"https://{_zarinpal_domain()}.zarinpal.com/pg/StartPay/"


def zarinpal_verify_url() -> str:
    return f"https://{_zarinpal_domain()}.zarinpal.com/pg/v4/payment/verify.json"
