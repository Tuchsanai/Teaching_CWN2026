# กติกา: amount = สตางค์ (>=0, int) ; 100 บาท = 10000 ; cap 200 บาท = 20000
# ขั้นตอน: amount < 10000 -> 0 ; amount * rate ; เดือนเกิด x2 ; cap 20000 ; ปัดครึ่งขึ้นเป็นสตางค์ท้ายสุด
from fractions import Fraction


class InvalidInput(ValueError, TypeError, KeyError):
    def __str__(self):
        return Exception.__str__(self)


_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise InvalidInput("amount must be int >= 0")
    if type(tier) is not str or tier not in _RATES:
        raise InvalidInput("invalid tier")
    if type(birthday) is not bool:
        raise InvalidInput("birthday must be bool")
    if amount < 10000:
        return 0
    v = amount * _RATES[tier] * (2 if birthday else 1)
    v = min(v, Fraction(20000))
    return (2 * v.numerator + v.denominator) // (2 * v.denominator)
