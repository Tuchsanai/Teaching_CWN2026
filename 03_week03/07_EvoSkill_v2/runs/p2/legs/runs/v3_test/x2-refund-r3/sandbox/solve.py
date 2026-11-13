# rounding policy r3 (banker's / half-even, exact Fraction)
from fractions import Fraction


def refund(paid, used_percent, restock):
    if type(paid) is not int or type(used_percent) is not int or type(restock) is not bool:
        raise ValueError("invalid input type")
    if paid < 0 or not (0 <= used_percent <= 100):
        raise ValueError("input out of range")
    if used_percent > 80:
        return 0
    amount = Fraction(paid * (100 - used_percent), 100)
    if restock:
        amount *= Fraction(875, 1000)
    return int(round(amount))
