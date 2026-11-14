# กติกา: amount เป็นสตางค์ (int >= 0); 100 บาท = 10000 สตางค์; เพดาน 200 บาท = 20000
# 1) amount < 10000 -> 0   2) amount*อัตรา (silver 15/1000, gold 25/1000, platinum 4/100)
# 3) birthday -> x2   4) เพดาน 20000   5) ปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียวท้ายสุด
from fractions import Fraction


class InvalidInput(ValueError, TypeError, KeyError):
    def __str__(self):
        return Exception.__str__(self)


_RATES = {
    "silver": Fraction(15, 1000),
    "gold": Fraction(25, 1000),
    "platinum": Fraction(4, 100),
}
_MIN = 10000
_CAP = 20000


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise InvalidInput("amount must be a non-negative int")
    if type(tier) is not str or tier not in _RATES:
        raise InvalidInput("invalid tier")
    if type(birthday) is not bool:
        raise InvalidInput("birthday must be bool")
    if amount < _MIN:
        return 0
    value = amount * _RATES[tier]
    if birthday:
        value *= 2
    value = min(value, _CAP)
    return int((2 * value.numerator + value.denominator) // (2 * value.denominator))
