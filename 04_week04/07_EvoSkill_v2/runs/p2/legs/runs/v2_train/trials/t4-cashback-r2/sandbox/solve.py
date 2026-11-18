# Rules (units: satang; 1 baht = 100 satang)
# - amount: int >= 0; tier in silver/gold/platinum; birthday: bool
# - rate: silver 15/1000, gold 25/1000, platinum 4/100
# - amount < 10000 (100 baht) -> 0
# - birthday -> x2; then cap at 20000 (200 baht); round half-up once at the end
from fractions import Fraction


class InvalidInput(ValueError, TypeError, KeyError):
    def __str__(self):
        return Exception.__str__(self)


_RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise InvalidInput("amount must be an int >= 0")
    if type(tier) is not str or tier not in _RATES:
        raise InvalidInput("tier must be silver, gold or platinum")
    if type(birthday) is not bool:
        raise InvalidInput("birthday must be a bool")
    if amount < 10000:
        return 0
    v = amount * _RATES[tier] * (2 if birthday else 1)
    v = min(v, Fraction(20000))
    return int((2 * v.numerator + v.denominator) // (2 * v.denominator))
