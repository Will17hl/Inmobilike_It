from decimal import Decimal, InvalidOperation


def normalize_decimal_input(value):
    if value is None:
        return ""

    normalized = str(value).strip().replace(" ", "")
    if not normalized:
        return ""

    if "," in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    else:
        dot_count = normalized.count(".")
        if dot_count > 1:
            normalized = normalized.replace(".", "")

    try:
        Decimal(normalized)
    except (InvalidOperation, ValueError):
        return ""

    return normalized
