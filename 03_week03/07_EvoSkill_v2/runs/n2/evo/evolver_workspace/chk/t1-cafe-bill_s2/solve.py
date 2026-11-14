from fractions import Fraction


def _half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def cafe_bill(items, member):
    if type(items) is not list or type(member) is not bool:
        raise ValueError("invalid input")
    subtotal = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("invalid item")
        p, q = it["price"], it["qty"]
        if type(p) is not int or type(q) is not int or p < 0 or q < 1:
            raise ValueError("invalid price/qty")
        subtotal += p * q
    total = Fraction(subtotal)
    if subtotal >= 50000:  # 500 baht, compared on pre-discount subtotal
        total *= Fraction(95, 100)
    if member:
        total *= Fraction(90, 100)
    total *= Fraction(107, 100)
    return _half_up(total)  # single half-up rounding at the end
