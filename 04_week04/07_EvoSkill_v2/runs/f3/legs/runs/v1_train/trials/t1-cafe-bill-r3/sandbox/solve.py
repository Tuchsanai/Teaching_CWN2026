from fractions import Fraction


def _is_int(v):
    return type(v) is int


def cafe_bill(items, member):
    if type(member) is not bool:
        raise ValueError("member must be bool")
    if type(items) is not list:
        raise ValueError("items must be list")
    subtotal = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("invalid item")
        p, q = it["price"], it["qty"]
        if not _is_int(p) or not _is_int(q) or p < 0 or q < 1:
            raise ValueError("invalid price/qty")
        subtotal += p * q
    x = Fraction(subtotal)
    if subtotal >= 50000:
        x *= Fraction(95, 100)
    if member:
        x *= Fraction(90, 100)
    x *= Fraction(107, 100)
    return int((x * 2 + 1) // 2)  # half-up, round once at the end
