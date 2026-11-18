# หน่วย: amount/ผลลัพธ์ = สตางค์ (int); 100 บาท = 10000; เพดาน 200 บาท = 20000
# ลำดับ: ตรวจอินพุต -> amount < 10000 ได้ 0 -> amount*rate -> x2 ถ้า birthday
#        -> เพดาน 20000 -> ปัดครึ่งขึ้นครั้งเดียวท้ายสุด
from fractions import Fraction

_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
_MIN = 10000
_CAP = 20000


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
        raise ValueError("amount must be an int >= 0")
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError("invalid tier")
    if not isinstance(birthday, bool):
        raise ValueError("birthday must be bool")
    if amount < _MIN:
        return 0
    v = amount * _RATES[tier]
    if birthday:
        v *= 2
    if v > _CAP:
        v = Fraction(_CAP)
    return int((2 * v.numerator + v.denominator) // (2 * v.denominator))
