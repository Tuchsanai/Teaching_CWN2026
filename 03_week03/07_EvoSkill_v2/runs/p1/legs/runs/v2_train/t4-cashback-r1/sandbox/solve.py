from fractions import Fraction


class InputError(ValueError, TypeError):
    """Invalid input (both ValueError and TypeError)."""


_RATES = {
    "silver": Fraction(15, 1000),   # 1.5%
    "gold": Fraction(25, 1000),     # 2.5%
    "platinum": Fraction(4, 100),   # 4%
}
_MIN_AMOUNT = 10000   # 100 baht in satang
_CAP = 20000          # 200 baht in satang


def cashback(amount, tier, birthday):
    # Validate all inputs first.
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise InputError(f"amount must be an int, got {amount!r}")
    if amount < 0:
        raise InputError("amount must be >= 0")
    if not isinstance(tier, str) or tier not in _RATES:
        raise InputError(f"unknown tier {tier!r}")
    if not isinstance(birthday, bool):
        raise InputError(f"birthday must be a bool, got {birthday!r}")

    # Assumptions: threshold on raw amount; birthday x2 applied before cap;
    # round half up once on the final value.
    if amount < _MIN_AMOUNT:
        return 0
    value = amount * _RATES[tier] * (2 if birthday else 1)
    value = min(value, _CAP)
    return (2 * value.numerator + value.denominator) // (2 * value.denominator)
