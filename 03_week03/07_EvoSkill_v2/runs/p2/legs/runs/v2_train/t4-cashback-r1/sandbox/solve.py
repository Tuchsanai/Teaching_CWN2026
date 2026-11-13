# validation policy r1
from fractions import Fraction

_RATES = {
    "silver": Fraction(15, 1000),
    "gold": Fraction(25, 1000),
    "platinum": Fraction(4, 100),
}
_MIN_AMOUNT = 10000  # 100 บาท
_CAP = 20000         # 200 บาท


def cashback(amount, tier, birthday):
    if type(amount) is not int:
        raise ValueError("amount must be int")
    if not isinstance(tier, str):
        raise ValueError("tier must be str")
    if not isinstance(birthday, bool):
        raise ValueError("birthday must be bool")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if tier not in _RATES:
        raise ValueError("invalid tier")
    if amount < _MIN_AMOUNT:
        return 0
    value = amount * _RATES[tier] * (2 if birthday else 1)
    if value > _CAP:
        value = Fraction(_CAP)
    return (value.numerator * 2 + value.denominator) // (value.denominator * 2)
