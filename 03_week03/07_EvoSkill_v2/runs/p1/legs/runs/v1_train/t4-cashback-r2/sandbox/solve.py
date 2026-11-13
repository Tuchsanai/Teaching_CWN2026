from fractions import Fraction

_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
_MIN_AMOUNT = 10000  # 100 baht in satang
_CAP = 20000         # 200 baht in satang


def _round_half_up(x):
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int):
        if isinstance(amount, float) and amount.is_integer() and amount >= 0:
            amount = int(amount)
        else:
            raise ValueError(f"amount must be a non-negative int, got {amount!r}")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError(f"unknown tier: {tier!r}")
    if not isinstance(birthday, bool):
        raise ValueError("birthday must be a bool")
    if amount < _MIN_AMOUNT:
        return 0
    value = amount * _RATES[tier]
    if birthday:
        value *= 2
    return min(_round_half_up(value), _CAP)
