from fractions import Fraction


def _need_int(v):
    if type(v) is not int:
        raise ValueError("must be int")
    return v


def split_bill(total, people, tip_percent):
    _need_int(total)
    _need_int(people)
    _need_int(tip_percent)
    if total < 0 or people < 1 or not (0 <= tip_percent <= 100):
        raise ValueError("out of range")
    # assumption: half-up rounding once on grand total (tip not rounded separately)
    grand = int((Fraction(total * (100 + tip_percent), 100) * 2 + 1) // 2)
    base, extra = divmod(grand, people)
    return [base + 1] * extra + [base] * (people - extra)
