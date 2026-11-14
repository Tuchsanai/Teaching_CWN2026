from fractions import Fraction


def _half_up(x):
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def _is_int(v):
    return type(v) is int


def split_bill(total, people, tip_percent):
    if not (_is_int(total) and _is_int(people) and _is_int(tip_percent)):
        raise ValueError("inputs must be int")
    if total < 0 or people < 1 or not (0 <= tip_percent <= 100):
        raise ValueError("input out of range")
    grand = _half_up(Fraction(total * (100 + tip_percent), 100))
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
