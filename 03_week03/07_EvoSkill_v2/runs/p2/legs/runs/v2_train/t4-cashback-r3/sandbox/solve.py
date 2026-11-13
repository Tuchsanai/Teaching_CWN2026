# validation policy r3
from fractions import Fraction
import math

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
MIN_AMOUNT = 10000  # 100 บาท
CAP = 20000  # 200 บาท


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise TypeError("amount must be a number")
    if not isinstance(tier, str):
        raise TypeError("tier must be a str")
    if not isinstance(birthday, bool):
        raise TypeError("birthday must be a bool")
    if isinstance(amount, float) and not math.isfinite(amount):
        raise ValueError("amount must be finite")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if tier not in RATES:
        raise ValueError("invalid tier")
    if amount < MIN_AMOUNT:
        return 0
    value = Fraction(amount) * RATES[tier] * (2 if birthday else 1)
    value = min(value, Fraction(CAP))
    return int((2 * value.numerator + value.denominator) // (2 * value.denominator))
