from fractions import Fraction

# นโยบายปัดเศษ r1: คำนวณแบบแม่นยำ (Fraction) แล้วปัดครึ่งขึ้นครั้งเดียวตอนท้าย
_RATES = {
    "silver": Fraction(15, 1000),
    "gold": Fraction(25, 1000),
    "platinum": Fraction(4, 100),
}
_MIN_AMOUNT = 10000  # 100 บาท
_CAP = 20000         # 200 บาท


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
        raise ValueError("amount must be an int >= 0")
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError("invalid tier")
    if not isinstance(birthday, bool):
        raise ValueError("birthday must be bool")
    if amount < _MIN_AMOUNT:
        return 0
    value = amount * _RATES[tier]
    if birthday:
        value *= 2
    value = min(value, _CAP)
    return int((value * 2 + 1) // 2)  # half-up
