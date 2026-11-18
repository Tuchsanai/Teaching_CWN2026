from fractions import Fraction


class InvalidInput(ValueError, TypeError):
    pass


def late_fee(amount, days_late):
    if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
        raise InvalidInput("amount must be an int >= 0")
    if isinstance(days_late, bool) or not isinstance(days_late, int) or not (0 <= days_late <= 365):
        raise InvalidInput("days_late must be an int in 0..365")
    if days_late <= 3:
        return 0
    fee = Fraction(amount * days_late * 75, 10000)
    cap = Fraction(amount * 15, 100)
    if fee > cap:
        fee = cap
    n, d = fee.numerator, fee.denominator
    return (2 * n + d) // (2 * d)
