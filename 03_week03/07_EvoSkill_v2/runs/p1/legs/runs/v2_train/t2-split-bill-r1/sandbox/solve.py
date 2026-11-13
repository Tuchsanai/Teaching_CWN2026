from fractions import Fraction


class InputError(ValueError, TypeError):
    """Invalid input: both ValueError and TypeError."""


def _check_int(name, v, lo, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise InputError(f"{name} must be an int, got {v!r}")
    if v < lo:
        raise InputError(f"{name} must be >= {lo}")
    if hi is not None and v > hi:
        raise InputError(f"{name} must be <= {hi}")
    return v


def _round_half_up(x):
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def split_bill(total, people, tip_percent):
    # Assumptions: tip = total * tip_percent / 100, rounded half-up once to
    # whole satang; grand total = total + tip; the remainder satang go to the
    # first people, 1 each.
    _check_int("total", total, 0)
    _check_int("people", people, 1)
    _check_int("tip_percent", tip_percent, 0, 100)
    tip = _round_half_up(Fraction(total * tip_percent, 100))
    grand = total + tip
    base, rem = divmod(grand, people)
    return [base + 1 if i < rem else base for i in range(people)]
