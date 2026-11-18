# หน่วย: amount/ผลลัพธ์ = สตางค์ (int) · 1 บาท = 100 สตางค์
# ลำดับ: ตรวจอินพุต -> amount < 10000 ได้ 0 -> amount*อัตรา -> x2 ถ้าเดือนเกิด
#        -> ปัดครึ่งขึ้นเป็นสตางค์ -> จำกัดสูงสุด 20000 สตางค์ (200 บาท)
from fractions import Fraction

_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
_MIN = 10000
_CAP = 20000


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be an int >= 0")
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError("tier must be silver, gold or platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")
    if amount < _MIN:
        return 0
    v = amount * _RATES[tier] * (2 if birthday else 1)
    r = (2 * v.numerator + v.denominator) // (2 * v.denominator)
    return int(min(r, _CAP))
