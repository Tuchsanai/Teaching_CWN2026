from fractions import Fraction
import math

_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(40, 1000)}


def cashback(amount, tier, birthday):
    if tier not in _RATES:
        raise ValueError("invalid tier")
    if amount < 10000:
        return 0
    r = Fraction(amount) * _RATES[tier]
    if birthday:
        r *= 2
    return min(math.ceil(r), 20000)
