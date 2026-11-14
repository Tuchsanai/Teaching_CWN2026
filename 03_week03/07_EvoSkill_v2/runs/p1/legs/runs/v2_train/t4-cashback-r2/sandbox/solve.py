from fractions import Fraction

RATES = {
    "silver": Fraction(15, 1000),   # 1.5%
    "gold": Fraction(25, 1000),     # 2.5%
    "platinum": Fraction(4, 100),   # 4%
}
MIN_AMOUNT = 10000  # 100 baht in satang
CAP = 20000         # 200 baht in satang


def cashback(amount, tier, birthday):
    # input validation (before any calculation)
    if not isinstance(amount, int) or isinstance(amount, bool):
        raise ValueError("amount must be an int")
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not isinstance(tier, str) or tier not in RATES:
        raise ValueError("tier must be 'silver', 'gold' or 'platinum'")
    if not isinstance(birthday, bool):
        raise ValueError("birthday must be a bool")

    if amount < MIN_AMOUNT:
        return 0
    value = Fraction(amount) * RATES[tier]
    if birthday:
        value *= 2
    # floor once at the end, then apply the cap
    result = value.numerator // value.denominator
    return int(min(result, CAP))
