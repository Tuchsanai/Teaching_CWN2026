from fractions import Fraction


def _rnd_even(x):
    """ปัดใกล้สุด เศษ .5 พอดีปัดไปหาเลขคู่ (เหมือน round()) — ปัดครั้งเดียวตอนจบ"""
    x = Fraction(x)
    q, r = divmod(x.numerator, x.denominator)
    twice = 2 * r
    if twice > x.denominator or (twice == x.denominator and q % 2 == 1):
        q += 1
    return q


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def bulk_price(unit_price, qty, coupon):
    if not _is_int(unit_price) or unit_price < 0:
        raise ValueError("unit_price must be int >= 0")
    if not _is_int(qty) or not (1 <= qty <= 1000):
        raise ValueError("qty must be int in 1..1000")
    if not isinstance(coupon, bool):
        raise ValueError("coupon must be bool")

    total = Fraction(unit_price * qty)
    if qty >= 50:
        total *= Fraction(1000 - 75, 1000)   # ลด 7.5%
    elif qty >= 10:
        total *= Fraction(1000 - 35, 1000)   # ลด 3.5%
    if coupon:
        total *= Fraction(1000 - 25, 1000)   # ลดอีก 2.5%
    total *= Fraction(107, 100)              # VAT 7% ขั้นสุดท้าย
    return int(_rnd_even(total))
