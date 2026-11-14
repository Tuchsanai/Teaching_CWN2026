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
    amt = total
    if total >= 50000:  # 500 บาท = 50000 สตางค์ (เทียบยอดก่อนลด)
        amt = _rnd(Fraction(amt) * 95 / 100)
    if member:
        amt = _rnd(Fraction(amt) * 90 / 100)
    amt = _rnd(Fraction(amt) * 107 / 100)  # VAT ขั้นสุดท้าย
    return int(amt)
