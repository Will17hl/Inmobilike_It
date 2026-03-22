from decimal import Decimal, InvalidOperation

from django import template


register = template.Library()


@register.filter
def currency_es(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return value

    normalized = amount.quantize(Decimal("0.01"))
    if normalized == normalized.to_integral():
        integer_part = f"{int(normalized):,}".replace(",", ".")
        return f"${integer_part}"

    formatted = f"{normalized:,.2f}"
    integer_part, decimal_part = formatted.split(".")
    integer_part = integer_part.replace(",", ".")
    return f"${integer_part},{decimal_part}"
