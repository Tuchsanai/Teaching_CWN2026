# validation policy r2
from fractions import Fraction


def cafe_bill(items, member):
    total = Fraction(0)
    for it in items:
        price, qty = it["price"], it["qty"]
        if qty < 1:
            raise ValueError("qty must be >= 1")
        if price < 0:
            raise ValueError("price must be >= 0")
        total += Fraction(price) * Fraction(qty)

    amount = total
    if total >= 50000:  # 500 baht, judged on the raw subtotal
        amount = amount * 95 / 100
    if member:
        amount = amount * 90 / 100
    amount = amount * 107 / 100

    # half-up rounding once, at the end
    return int((amount * 2 + 1) // 2)
