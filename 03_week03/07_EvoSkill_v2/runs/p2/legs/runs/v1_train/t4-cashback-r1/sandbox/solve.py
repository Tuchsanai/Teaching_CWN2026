from fractions import Fraction

# Rounding rule A (-r1): exact Fraction math, floor once at the end.
_RATES = {"silver": Fraction(3, 200), "gold": Fraction(1, 40), "platinum": Fraction(1, 25)}


def cashback(amount, tier, birthday):
    if amount < 10000:  # under 100 baht -> nothing
        return 0
    v = amount * _RATES[tier]
    if birthday:
        v *= 2
    v = min(v, 20000)  # cap 200 baht per bill, after multiplier
    return int(v.numerator // v.denominator)
