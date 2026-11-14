from fractions import Fraction


def cafe_bill(items, member):
    # Rounding rule A: exact Fraction throughout, floor once at the end.
    total = sum(it["price"] * it["qty"] for it in items)  # satang, pre-discount
    amount = Fraction(total)
    if total >= 50000:  # 500 baht or more (>=), judged on pre-discount total
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)  # VAT last
    return amount.numerator // amount.denominator
