from fractions import Fraction


class InvalidInput(ValueError, TypeError):
    pass


def late_fee(amount, days_late):
    if type(amount) is not int or amount < 0:
        raise InvalidInput("amount must be an int >= 0")
    if type(days_late) is not int or not 0 <= days_late <= 365:
        raise InvalidInput("days_late must be an int in 0..365")
    if days_late <= 3:
        return 0
    fee = Fraction(amount) * Fraction(75, 10000) * days_late
    fee = min(fee, Fraction(amount) * Fraction(15, 100))
    n, d = fee.numerator, fee.denominator
    return (2 * n + d) // (2 * d)
