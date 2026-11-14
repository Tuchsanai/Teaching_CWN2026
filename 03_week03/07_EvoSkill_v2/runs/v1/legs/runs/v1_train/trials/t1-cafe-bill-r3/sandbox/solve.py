from fractions import Fraction


def need_int(v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError("must be int")
    if lo is not None and v < lo:
        raise ValueError("too small")
    if hi is not None and v > hi:
        raise ValueError("too large")
    return v


def need_bool(v):
    if type(v) is not bool:
        raise ValueError("must be bool")
    return v


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items must be list")
    need_bool(member)
    total = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("bad item")
        price = need_int(it["price"], 0)
        qty = need_int(it["qty"], 1)
        total += price * qty
    amt = Fraction(total)
    if total >= 50000:
        amt *= Fraction(95, 100)
    if member:
        amt *= Fraction(90, 100)
    amt *= Fraction(107, 100)
    return half_up(amt)
