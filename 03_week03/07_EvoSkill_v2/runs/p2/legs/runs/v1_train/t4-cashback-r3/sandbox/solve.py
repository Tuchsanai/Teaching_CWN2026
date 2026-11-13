# นโยบายปัดเศษ r3: คำนวณแม่นยำด้วยจำนวนเต็ม/เศษส่วน แล้วปัดลง (floor) ครั้งเดียวตอนท้าย
from fractions import Fraction

_RATES = {
    "silver": Fraction(15, 1000),
    "gold": Fraction(25, 1000),
    "platinum": Fraction(4, 100),
}
_MIN_AMOUNT = 100 * 100   # 100 บาท (สตางค์)
_CAP = 200 * 100          # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
        raise ValueError("amount must be a non-negative int (satang)")
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError("tier must be 'silver', 'gold' or 'platinum'")
    if not isinstance(birthday, bool):
        raise ValueError("birthday must be bool")
    if amount < _MIN_AMOUNT:
        return 0
    value = amount * _RATES[tier]
    if birthday:
        value *= 2
    return min(int(value // 1), _CAP)  # floor ครั้งเดียว แล้วจำกัดเพดาน
