# validation policy r3
from fractions import Fraction


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    if not isinstance(items, (list, tuple)):
        raise TypeError("items must be a list")
    if not isinstance(member, bool):
        raise TypeError("member must be bool")
    if len(items) == 0:
        raise ValueError("items must not be empty")
    total = 0
    for it in items:
        if not isinstance(it, dict):
            raise TypeError("item must be a dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("item needs price and qty")
        p, q = it["price"], it["qty"]
        if not _is_int(p) or not _is_int(q):
            raise TypeError("price and qty must be int")
        if p < 0:
            raise ValueError("price must be >= 0")
        if q < 1:
            raise ValueError("qty must be >= 1")
        total += p * q
    amt = Fraction(total)
    if total >= 50000:
        amt = amt * 95 / 100
    if member:
        amt = amt * 90 / 100
    amt = amt * 107 / 100
    return int((amt * 2 + 1) // 2)
