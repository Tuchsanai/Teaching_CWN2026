from fractions import Fraction


class InputError(ValueError, TypeError):
    """Invalid input (both ValueError and TypeError)."""


def _round_half_up(x):
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def _check_int(name, v, lo):
    if isinstance(v, bool) or not isinstance(v, int):
        raise InputError(f"{name} must be an int, got {v!r}")
    if v < lo:
        raise InputError(f"{name} must be >= {lo}")
    return v


def cafe_bill(items, member):
    # Assumptions: threshold (>= 500 baht = 50000 satang) uses raw subtotal;
    # discounts compound (5% then 10%), VAT last; round half up once at the end.
    if not isinstance(items, (list, tuple)):
        raise InputError("items must be a list or tuple")
    if not isinstance(member, bool):
        raise InputError("member must be a bool")
    total = 0
    for it in items:
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise InputError("each item must be a dict with price and qty")
        total += _check_int("price", it["price"], 0) * _check_int("qty", it["qty"], 1)
    amount = Fraction(total)
    if total >= 50000:
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)
    return _round_half_up(amount)
