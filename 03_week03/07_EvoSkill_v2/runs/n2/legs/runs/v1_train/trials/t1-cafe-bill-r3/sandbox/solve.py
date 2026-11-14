from fractions import Fraction


def _need_int(v):
    if type(v) is not int:
        raise ValueError("must be int")
    return v


def cafe_bill(items, member):
    # Assumptions: money in satang; rounding half-up once at the end;
    # 5% threshold compares pre-discount subtotal >= 50000 satang.
    if type(items) is not list:
        raise ValueError("items must be list")
    if type(member) is not bool:
        raise ValueError("member must be bool")
    sub = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("bad item")
        p, q = _need_int(it["price"]), _need_int(it["qty"])
        if p < 0 or q < 1:
            raise ValueError("bad price/qty")
        sub += p * q
    x = Fraction(sub)
    if sub >= 50000:
        x *= Fraction(95, 100)
    if member:
        x *= Fraction(90, 100)
    x *= Fraction(107, 100)
    return int((x * 2 + 1) // 2)
