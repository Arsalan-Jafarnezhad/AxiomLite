from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError

def automatic_score(passed, total):
    if not total:
        raise ValidationError("Automatic evaluation requires at least one active test.")
    return (Decimal(passed) * Decimal("100") / Decimal(total)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
