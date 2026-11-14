from fractions import Fraction


def _rnd(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์"""
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def split_bill(total, people, tip_percent):
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if tip_percent < 0 or tip_percent > 100:
        raise ValueError("tip_percent must be in 0..100")
    # ยอดรวมทิป ปัดครึ่งขึ้นเป็นสตางค์เต็ม
    grand = _rnd(Fraction(total) * (100 + tip_percent) / 100)
    base, extra = divmod(grand, people)
    return [int(base + 1) if i < extra else int(base) for i in range(people)]
