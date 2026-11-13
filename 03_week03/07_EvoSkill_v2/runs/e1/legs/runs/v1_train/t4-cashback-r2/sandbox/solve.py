from fractions import Fraction

_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}


def _half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม >= 0")
    if type(tier) is not str or tier not in _RATES:
        raise ValueError("tier ไม่ถูกต้อง")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True/False")
    if amount < 10000:
        return 0
    v = amount * _RATES[tier] * (2 if birthday else 1)
    return min(20000, _half_up(v))
