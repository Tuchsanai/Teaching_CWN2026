# rounding policy r3 (banker's / half-even, exact, rounded once at the end)
from fractions import Fraction


def bulk_price(unit_price, qty, coupon):
    if type(unit_price) is not int or type(qty) is not int or type(coupon) is not bool:
        raise ValueError("invalid input type")
    if unit_price < 0 or not (1 <= qty <= 1000):
        raise ValueError("value out of range")

    total = Fraction(unit_price * qty)
    if qty >= 50:
        total *= Fraction(1000 - 75, 1000)
    elif qty >= 10:
        total *= Fraction(1000 - 35, 1000)
    if coupon:
        total *= Fraction(1000 - 25, 1000)
    total *= Fraction(107, 100)
    return int(round(total))  # Fraction round() is half-even -> int
