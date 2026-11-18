from fractions import Fraction


def _is_int(v):
    return type(v) is int


def split_bill(total, people, tip_percent):
    if not _is_int(total) or total < 0:
        raise ValueError("total must be int >= 0")
    if not _is_int(people) or people < 1:
        raise ValueError("people must be int >= 1")
    if not _is_int(tip_percent) or not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent must be int in 0..100")
    # customer pays shop -> round half-up, once
    x = Fraction(total * (100 + tip_percent), 100)
    grand = int((x * 2 + 1) // 2)
    base, extra = divmod(grand, people)
    return [base + 1] * extra + [base] * (people - extra)
