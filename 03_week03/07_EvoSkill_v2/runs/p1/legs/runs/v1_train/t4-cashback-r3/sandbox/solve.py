from fractions import Fraction

_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
_MIN_AMOUNT = 10000   # 100 baht in satang
_CAP = 20000          # 200 baht in satang


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError(f"amount must be an int, got {amount!r}")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError(f"unknown tier: {tier!r}")
    if not isinstance(birthday, bool):
        raise ValueError(f"birthday must be a bool, got {birthday!r}")
    if amount < _MIN_AMOUNT:
        return 0
    value = amount * _RATES[tier] * (2 if birthday else 1)
    cents = (2 * value.numerator + value.denominator) // (2 * value.denominator)
    return int(min(cents, _CAP))
