from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.utils.translation import get_language


def uses_uah():
    """Ukrainian pages show hryvnia. English pages show dollars."""
    return (get_language() or "en").lower().startswith("uk")


def _rate():
    return Decimal(settings.UAH_PER_USD)


def usd_to_uah(amount):
    return (Decimal(amount) * _rate()).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def uah_to_usd(amount):
    return (Decimal(amount) / _rate()).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def format_money(amount):
    """Format a price stored in US dollars for the active language."""
    amount = Decimal(amount)
    if uses_uah():
        return _grouped(usd_to_uah(amount), " ") + " грн"
    quantized = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    text = f"{quantized:.2f}"
    if text.endswith(".00"):
        text = text[:-3]
    elif text.endswith("0"):
        text = text[:-1]
    return f"${text}"


def _grouped(amount, separator):
    quantized = Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    sign = "-" if quantized < 0 else ""
    whole, frac = f"{abs(quantized):.2f}".split(".")
    parts = []
    while whole:
        parts.append(whole[-3:])
        whole = whole[:-3]
    text = separator.join(reversed(parts))
    if frac != "00":
        text = f"{text},{frac}"
    return f"{sign}{text}"
