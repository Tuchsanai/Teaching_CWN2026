from fractions import Fraction


def _rnd_even(x):
    # ปัดครั้งเดียวตอนจบ แบบเดียวกับ round() ของ Python (เศษ .5 ปัดไปหาเลขคู่)
    x = Fraction(x)
    q, r = divmod(x.numerator, x.denominator)
    if 2 * r > x.denominator or (2 * r == x.denominator and q % 2 == 1):
        q += 1
    return q


def refund(paid, used_percent, restock):
    if not isinstance(paid, int) or isinstance(paid, bool) or paid < 0:
        raise ValueError("paid must be int >= 0")
    if (not isinstance(used_percent, int) or isinstance(used_percent, bool)
            or not 0 <= used_percent <= 100):
        raise ValueError("used_percent must be int 0-100")
    if not isinstance(restock, bool):
        raise ValueError("restock must be bool")
    if used_percent > 80:
        return 0
    amt = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amt *= Fraction(875, 1000)  # หัก 12.5% ของยอดที่จะคืน
    return int(_rnd_even(amt))
