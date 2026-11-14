from fractions import Fraction


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if not isinstance(member, bool):
        raise ValueError("member must be bool")
    total = 0
    for it in items:
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise ValueError("invalid item")
        p, q = it["price"], it["qty"]
        if not _is_int(p) or p < 0:
            raise ValueError("invalid price")
        if not _is_int(q) or q < 1:
            raise ValueError("invalid qty")
        total += p * q
    amt = Fraction(total)
    if total >= 50000:  # 500 baht, based on pre-discount total
        amt *= Fraction(95, 100)
    if member:
        amt *= Fraction(90, 100)
    amt *= Fraction(107, 100)  # VAT last
    # no intermediate rounding; floor once at the end (per skill policy)
    return amt.numerator // amt.denominator
