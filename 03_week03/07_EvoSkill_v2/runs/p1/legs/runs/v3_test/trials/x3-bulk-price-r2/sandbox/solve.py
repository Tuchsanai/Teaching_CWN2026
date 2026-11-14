from fractions import Fraction


class InvalidInput(ValueError, TypeError):
    pass


def bulk_price(unit_price, qty, coupon):
    if type(unit_price) is not int or unit_price < 0:
        raise InvalidInput("unit_price must be int >= 0")
    if type(qty) is not int or not (1 <= qty <= 1000):
        raise InvalidInput("qty must be int in 1..1000")
    if not isinstance(coupon, bool):
        raise InvalidInput("coupon must be bool")
    v = Fraction(unit_price * qty)
    if qty >= 50:
        v *= 1 - Fraction(75, 1000)
    elif qty >= 10:
        v *= 1 - Fraction(35, 1000)
    if coupon:
        v *= 1 - Fraction(25, 1000)
    v *= Fraction(107, 100)
    return (2 * v.numerator + v.denominator) // (2 * v.denominator)
