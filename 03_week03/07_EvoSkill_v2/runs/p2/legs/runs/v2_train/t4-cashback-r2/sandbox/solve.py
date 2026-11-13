# validation policy r2
from fractions import Fraction

_RATES = {
    "silver": Fraction(15, 1000),
    "gold": Fraction(25, 1000),
    "platinum": Fraction(4, 100),
}
_MIN_AMOUNT = 10000   # 100 baht
_CAP = 20000          # 200 baht


def cashback(amount, tier, birthday):
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if tier not in _RATES:
        raise ValueError("invalid tier")
    if amount < _MIN_AMOUNT:
        return 0
    value = Fraction(amount) * _RATES[tier] * (2 if birthday else 1)
    value = min(value, _CAP)
    return int((2 * value.numerator + value.denominator) // (2 * value.denominator))
