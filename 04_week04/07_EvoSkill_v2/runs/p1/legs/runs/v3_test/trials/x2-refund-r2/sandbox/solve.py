from fractions import Fraction


class InvalidInput(ValueError, TypeError):
    pass


def refund(paid, used_percent, restock):
    if type(paid) is not int or paid < 0:
        raise InvalidInput("paid must be int >= 0")
    if type(used_percent) is not int or not 0 <= used_percent <= 100:
        raise InvalidInput("used_percent must be int 0-100")
    if type(restock) is not bool:
        raise InvalidInput("restock must be bool")
    if used_percent > 80:
        return 0
    v = Fraction(paid * (100 - used_percent), 100)
    if restock:
        v *= Fraction(875, 1000)
    n, d = v.numerator, v.denominator
    return (2 * n + d) // (2 * d)
