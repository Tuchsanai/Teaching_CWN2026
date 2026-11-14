from fractions import Fraction

_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}


def cashback(amount, tier, birthday):
    # Validate types and ranges
    if not isinstance(amount, int) or isinstance(amount, bool):
        raise ValueError("amount must be int")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError("invalid tier")
    if not isinstance(birthday, bool):
        raise ValueError("birthday must be bool")
    if amount < 10000:  # under 100 baht: no cashback
        return 0
    x = amount * _RATES[tier] * (2 if birthday else 1)
    # Single floor at the end, then cap at 200 baht (20000 satang)
    return min(x.numerator // x.denominator, 20000)
