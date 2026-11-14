from fractions import Fraction


def split_bill(total, people, tip_percent):
    # Variant H: exact Fraction math, round-half-up once at the end, validate inputs.
    if total < 0:
        raise ValueError("total must be >= 0")
    if people < 1:
        raise ValueError("people must be >= 1")
    if tip_percent < 0 or tip_percent > 100:
        raise ValueError("tip_percent must be in 0..100")
    amount = Fraction(total) * (100 + Fraction(tip_percent)) / 100
    n, d = amount.numerator, amount.denominator
    grand = (2 * n + d) // (2 * d)
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]
