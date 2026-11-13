from fractions import Fraction

_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
_MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
_CAP = 20000          # 200 บาท (สตางค์)


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
    v = amount * _RATES[tier]
    if birthday:
        v *= 2
    v = min(v, _CAP)  # cap หลังคูณ 2
    return int((2 * v.numerator + v.denominator) // (2 * v.denominator))  # ครึ่งขึ้น ครั้งเดียว
