# กติกา: amount เป็นสตางค์ (int >= 0); 100 บาท = 10000 สตางค์; เพดาน 200 บาท = 20000
# ลำดับ: amount < 10000 -> 0; amount*rate; birthday x2; cap 20000; ปัดครึ่งขึ้นครั้งเดียวท้ายสุด
from fractions import Fraction

_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
        raise ValueError("amount must be an int >= 0")
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError("invalid tier")
    if not isinstance(birthday, bool):
        raise ValueError("birthday must be bool")
    if amount < 10000:
        return 0
    v = amount * _RATES[tier]
    if birthday:
        v *= 2
    v = min(v, Fraction(20000))
    return int((2 * v.numerator + v.denominator) // (2 * v.denominator))
