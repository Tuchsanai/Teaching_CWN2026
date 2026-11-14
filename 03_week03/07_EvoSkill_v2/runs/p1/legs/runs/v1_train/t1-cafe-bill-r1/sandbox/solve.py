from fractions import Fraction


def _rnd(x):
    """ปัดครึ่งขึ้นเป็นสตางค์เต็ม"""
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def cafe_bill(items, member):
    total = 0
    for it in items:
        price, qty = it["price"], it["qty"]
        if qty < 1:
            raise ValueError("qty must be >= 1")
        if price < 0:
            raise ValueError("price must be >= 0")
        total += price * qty
    # ปัดเศษทีละขั้นที่เป็นเปอร์เซ็นต์ (ครึ่งขึ้น)
    if total >= 50000:
        total = _rnd(Fraction(total) * 95 / 100)
    if member:
        total = _rnd(Fraction(total) * 90 / 100)
    total = _rnd(Fraction(total) * 107 / 100)
    return int(total)
