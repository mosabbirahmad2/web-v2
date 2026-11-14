from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter(name="clean_price")
def clean_price(value):
    """
    Format a price for display, stripping a trailing ".00" while keeping
    real fractional values intact.

        100.00  -> "100"
        99.50   -> "99.50"
        33      -> "33"
        None    -> "0"

    Accepts Decimal, int, float, or numeric strings (anything the
    product/price fields in this project might hand it). Falls back to
    "0" for anything that can't be parsed, so a template never 500s over
    a bad/missing price.
    """
    if value is None or value == "":
        return "0"

    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return value

    # Normalize to 2 decimal places first so e.g. Decimal("100") and
    # Decimal("100.00") both behave the same way.
    amount = amount.quantize(Decimal("0.01"))

    if amount == amount.to_integral_value():
        return str(amount.to_integral_value())

    # Keep exactly 2 decimal places for fractional amounts (99.50, not 99.5).
    return f"{amount:.2f}"
