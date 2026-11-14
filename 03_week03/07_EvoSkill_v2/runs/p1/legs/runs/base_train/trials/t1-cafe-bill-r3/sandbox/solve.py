from fractions import Fraction


def cafe_bill(items, member):
    total = sum(i["price"] * i["qty"] for i in items)  # satang
    amt = Fraction(total)
    if total >= 50000:  # 500 baht
        amt *= Fraction(95, 100)
    if member:
        amt *= Fraction(90, 100)
    amt *= Fraction(107, 100)
    # exact arithmetic, round half up once at the end
    return int((amt * 2 + 1) // 2)
