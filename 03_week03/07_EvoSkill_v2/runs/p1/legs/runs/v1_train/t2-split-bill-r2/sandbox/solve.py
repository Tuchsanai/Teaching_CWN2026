from fractions import Fraction


def _rnd(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์"""
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def split_bill(total, people, tip_percent):
    if isinstance(total, bool) or not isinstance(total, int) or total < 0:
        raise ValueError("total must be an integer >= 0")
    if isinstance(people, bool) or not isinstance(people, int) or people < 1:
        raise ValueError("people must be an integer >= 1")
    if isinstance(tip_percent, bool) or not isinstance(tip_percent, int) or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be an integer in 0..100")

    # ยอดรวม = ยอดบิล + ทิป ปัดครึ่งขึ้นเป็นสตางค์เต็ม
    grand = _rnd(Fraction(total * (100 + tip_percent), 100))
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
