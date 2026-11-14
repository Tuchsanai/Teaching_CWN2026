from fractions import Fraction


def late_fee(amount, days_late):
    # H2: any invalid input -> ValueError only
    for v in (amount, days_late):
        if isinstance(v, bool) or not isinstance(v, int):
            raise ValueError("amount and days_late must be integers")
    if amount < 0 or not (0 <= days_late <= 365):
        raise ValueError("input out of range")

    if days_late <= 3:
        return 0
    # 0.75% per day (all late days counted), capped at 15%; exact arithmetic
    fee = min(Fraction(amount * 75 * days_late, 10000), Fraction(amount * 15, 100))
    # round half up once at the end
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)
