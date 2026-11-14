from fractions import Fraction

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
MIN_AMOUNT = 10000   # 100 baht
CAP = 20000          # 200 baht


def _rnd(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์"""
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def cashback(amount, tier, birthday):
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if tier not in RATES:
        raise ValueError("unknown tier")
    if amount < MIN_AMOUNT:
        return 0
    cb = _rnd(amount * RATES[tier])   # ปัดเป็นสตางค์เต็มหลังคิดอัตรา
    if birthday:
        cb *= 2
    return int(min(cb, CAP))
