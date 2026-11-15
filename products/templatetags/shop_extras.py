from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter(name='clean_price')
def clean_price(value):
    """
    Renders a price without a trailing '.00' for whole numbers, while still
    showing real decimals: ৳100.00 -> "100", ৳99.50 -> "99.50".

    BUG FIX: every price on the storefront used to print Django's raw
    DecimalField value (e.g. "100.00", "33.00"), which looks unpolished next
    to genuinely fractional prices like "99.50". This keeps 2 decimals only
    when they're non-zero, and adds thousands separators either way.
    """
    if value is None or value == '':
        return value
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return value

    if amount == amount.to_integral_value():
        return f"{int(amount):,}"
    return f"{amount:,.2f}"
