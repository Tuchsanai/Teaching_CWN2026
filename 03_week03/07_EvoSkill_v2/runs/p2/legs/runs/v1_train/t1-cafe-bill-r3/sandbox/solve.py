from fractions import Fraction

# Rounding policy r3: exact arithmetic throughout, floor once at the end.


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    total = 0
    for it in items:
        price, qty = it["price"], it["qty"]
        if not _is_int(price) or price < 0:
            raise ValueError("price must be a non-negative int")
        if not _is_int(qty) or qty < 1:
            raise ValueError("qty must be an int >= 1")
        total += price * qty
    amount = Fraction(total)
    if total >= 50000:  # 500 baht, judged on the undiscounted total
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)
    return amount.numerator // amount.denominator
