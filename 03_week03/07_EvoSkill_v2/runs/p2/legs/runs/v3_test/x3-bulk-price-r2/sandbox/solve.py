# rounding policy r2 (ceiling at the end)
from fractions import Fraction


def bulk_price(unit_price, qty, coupon):
    if type(unit_price) is not int or type(qty) is not int or type(coupon) is not bool:
        raise ValueError("invalid input type")
    if unit_price < 0:
        raise ValueError("unit_price must be >= 0")
    if not 1 <= qty <= 1000:
        raise ValueError("qty must be 1..1000")

    total = Fraction(unit_price * qty)
    if qty >= 50:
        total *= Fraction(925, 1000)
    elif qty >= 10:
        total *= Fraction(965, 1000)
    if coupon:
        total *= Fraction(975, 1000)
    total *= Fraction(107, 100)
    return -(-total.numerator // total.denominator)
