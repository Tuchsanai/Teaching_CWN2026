from fractions import Fraction

# Rounding policy r1: exact Fraction arithmetic, half-up once at the end (on the total to split).


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def split_bill(total, people, tip_percent):
    if not (_is_int(total) and total >= 0):
        raise ValueError("total must be an int >= 0")
    if not (_is_int(people) and people >= 1):
        raise ValueError("people must be an int >= 1")
    if not (_is_int(tip_percent) and 0 <= tip_percent <= 100):
        raise ValueError("tip_percent must be an int in 0..100")
    exact = Fraction(total * (100 + tip_percent), 100)
    grand = (exact * 2 + 1) // 2  # half-up
    base, extra = divmod(int(grand), people)
    return [base + 1 if i < extra else base for i in range(people)]
