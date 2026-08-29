import re
from decimal import Decimal, InvalidOperation

def normalize_output(lines, mode):
    text = "\n".join(str(x) for x in lines)
    if mode == "trimmed":
        return text.strip()
    if mode == "case_insensitive":
        return text.lower()
    if mode == "whitespace_insensitive":
        return re.sub(r"\s+", "", text)
    return text

def compare_outputs(expected, actual, mode):
    if mode == "numeric":
        try:
            e = [Decimal(str(x)) for x in expected]
            a = [Decimal(str(x)) for x in actual]
            return e == a
        except (InvalidOperation, TypeError):
            return False
    return normalize_output(expected, mode) == normalize_output(actual, mode)

def clamp_score(value):
    value = Decimal(value).quantize(Decimal("0.01"))
    return max(Decimal("0.00"), min(Decimal("100.00"), value))
