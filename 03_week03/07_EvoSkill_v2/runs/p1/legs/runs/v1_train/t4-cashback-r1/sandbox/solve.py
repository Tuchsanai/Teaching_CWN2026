from fractions import Fraction

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}


def _rnd(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์"""
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def cashback(amount, tier, birthday):
    if tier not in RATES:
        raise ValueError("unknown tier")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if amount < 10000:  # ต่ำกว่า 100 บาท ไม่ได้เงินคืน
        return 0
    cb = _rnd(amount * RATES[tier])  # ปัดครึ่งขึ้นหลังคูณอัตรา
    if birthday:
        cb *= 2
    return int(min(cb, 20000))  # เพดาน 200 บาท
