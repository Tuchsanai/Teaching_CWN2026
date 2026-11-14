from fractions import Fraction

RATES = {
    "silver": Fraction(3, 200),
    "gold": Fraction(1, 40),
    "platinum": Fraction(1, 25),
}
MIN_AMOUNT = 10000  # 100 baht
CAP = 20000  # 200 baht


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be int >= 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")

    if amount < MIN_AMOUNT:
        return 0
    value = amount * RATES[tier]
    # house policy: birthday double applies to gold/platinum only
    if birthday and tier != "silver":
        value *= 2
    return min(value.numerator // value.denominator, CAP)
