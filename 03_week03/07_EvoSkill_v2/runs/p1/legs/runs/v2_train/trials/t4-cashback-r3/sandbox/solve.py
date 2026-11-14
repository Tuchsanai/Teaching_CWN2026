from fractions import Fraction
import math

_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(40, 1000)}
_MIN_AMOUNT = 10000  # 100 บาท
_CAP = 20000         # 200 บาท


def cashback(amount, tier, birthday):
    if tier not in _RATES:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if amount < _MIN_AMOUNT:
        return 0
    value = Fraction(amount) * _RATES[tier]
    if birthday:
        value *= 2
    return min(math.ceil(value), _CAP)
