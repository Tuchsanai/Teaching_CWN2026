# validation policy r1
from fractions import Fraction


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    if not isinstance(member, bool):
        raise ValueError("member must be bool")
    if not isinstance(items, (list, tuple)) or len(items) == 0:
        raise ValueError("items must be a non-empty list")
    total = 0
    for it in items:
        if not isinstance(it, dict):
            raise ValueError("item must be a dict")
        price, qty = it.get("price"), it.get("qty")
        if not _is_int(price) or not _is_int(qty):
            raise ValueError("price and qty must be int")
        if price < 0:
            raise ValueError("price must be >= 0")
        if qty < 1:
            raise ValueError("qty must be >= 1")
        total += price * qty

    amount = Fraction(total)
    if total >= 50000:
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)
    return (2 * amount.numerator + amount.denominator) // (2 * amount.denominator)
