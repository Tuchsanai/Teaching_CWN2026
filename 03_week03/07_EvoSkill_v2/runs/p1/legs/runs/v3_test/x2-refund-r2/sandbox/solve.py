from fractions import Fraction


def _rnd_even(x):
    """ปัดเป็นจำนวนเต็มแบบ round() ของ Python (ใกล้สุด, .5 พอดีปัดหาเลขคู่) ครั้งเดียวตอนจบ"""
    x = Fraction(x)
    q, r = divmod(x.numerator, x.denominator)
    twice = 2 * r
    if twice > x.denominator or (twice == x.denominator and q % 2 == 1):
        q += 1
    return q


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def refund(paid, used_percent, restock):
    if not _is_int(paid) or paid < 0:
        raise ValueError("paid must be int >= 0")
    if not _is_int(used_percent) or not 0 <= used_percent <= 100:
        raise ValueError("used_percent must be int 0-100")
    if not isinstance(restock, bool):
        raise ValueError("restock must be bool")

    if used_percent > 80:
        return 0
    amount = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amount *= Fraction(875, 1000)  # หัก 12.5%
    return int(_rnd_even(amount))
