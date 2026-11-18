from fractions import Fraction


def _need_int(v, lo):
    if type(v) is not int or v < lo:
        raise ValueError("invalid integer")
    return v


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items must be list")
    if type(member) is not bool:
        raise ValueError("member must be bool")
    total = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("invalid item")
        total += _need_int(it["price"], 0) * _need_int(it["qty"], 1)
    x = Fraction(total)
    if total >= 50000:
        x *= Fraction(95, 100)
    if member:
        x *= Fraction(90, 100)
    x *= Fraction(107, 100)
    return int((x * 2 + 1) // 2)
