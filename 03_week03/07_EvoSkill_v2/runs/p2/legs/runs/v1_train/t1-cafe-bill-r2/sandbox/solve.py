from fractions import Fraction

def cafe_bill(items, member):
    # Rule B: exact Fraction arithmetic, ceil once at the end
    total = sum(i["price"] * i["qty"] for i in items)
    x = Fraction(total)
    if total >= 50000:  # 500 baht, based on pre-discount total
        x *= Fraction(95, 100)
    if member:
        x *= Fraction(90, 100)
    x *= Fraction(107, 100)
    return -((-x.numerator) // x.denominator)
