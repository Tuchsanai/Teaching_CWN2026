from fractions import Fraction


def _round_half_up(x):
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def _check_int(name, v, lo):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be an int, got {v!r}")
    if v < lo:
        raise ValueError(f"{name} must be >= {lo}")
    return v


def cafe_bill(items, member):
    if not isinstance(member, bool):
        raise ValueError("member must be a bool")
    subtotal = 0
    for it in items:
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise ValueError("each item needs price and qty")
        price = _check_int("price", it["price"], 0)
        qty = _check_int("qty", it["qty"], 1)
        subtotal += price * qty
    total = Fraction(subtotal)
    if subtotal >= 50000:
        total *= Fraction(95, 100)
    if member:
        total *= Fraction(90, 100)
    total *= Fraction(107, 100)
    return _round_half_up(total)
