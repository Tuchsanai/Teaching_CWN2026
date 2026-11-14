from fractions import Fraction


def _rnd_even(x):
    """ปัดใกล้สุด เศษ .5 พอดีปัดไปหาเลขคู่ (เหมือน round()) ปัดครั้งเดียวตอนจบ"""
    x = Fraction(x)
    q, r = divmod(x.numerator, x.denominator)
    twice = 2 * r
    if twice > x.denominator or (twice == x.denominator and q % 2 == 1):
        q += 1
    return q


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def late_fee(amount, days_late):
    if not _is_int(amount) or amount < 0:
        raise ValueError("amount must be an int >= 0")
    if not _is_int(days_late) or not 0 <= days_late <= 365:
        raise ValueError("days_late must be an int in 0..365")
    if days_late <= 3:
        return 0
    fee = Fraction(amount * 75 * days_late, 10000)  # 0.75% ต่อวัน นับทุกวัน
    cap = Fraction(amount * 15, 100)                # เพดาน 15%
    return int(_rnd_even(min(fee, cap)))
