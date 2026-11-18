"""BaanKafe cashier: compute the amount a customer must pay.

Rules
- items: list of {"price": unit price in satang (int), "qty": count (int >= 1)}
- subtotal >= 50,000 satang (500 baht): 5% off
- member=True: a further 10% off (applied after the 5%)
- 7% VAT added last
- Returns the final amount as an integer number of satang.

All arithmetic uses Fraction, so no floating-point error creeps in.
The final amount is rounded half-up to the nearest satang.
"""

from fractions import Fraction
from math import floor

THRESHOLD_SATANG = 50_000  # 500 baht
BULK_DISCOUNT = Fraction(5, 100)
MEMBER_DISCOUNT = Fraction(10, 100)
VAT_RATE = Fraction(7, 100)


def cafe_bill(items, member):
    subtotal = 0
    for item in items:
        price = item["price"]
        qty = item["qty"]
        if not isinstance(price, int) or price < 0:
            raise ValueError(f"price must be a non-negative int (satang): {price!r}")
        if not isinstance(qty, int) or qty < 1:
            raise ValueError(f"qty must be an int >= 1: {qty!r}")
        subtotal += price * qty

    total = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:
        total *= 1 - BULK_DISCOUNT
    if member:
        total *= 1 - MEMBER_DISCOUNT
    total *= 1 + VAT_RATE

    # round half-up to the nearest satang
    return floor(total + Fraction(1, 2))


if __name__ == "__main__":
    # Subtotal 400 baht, not member: 400 * 1.07 = 428 baht
    assert cafe_bill([{"price": 40_000, "qty": 1}], False) == 42_800
    # Subtotal exactly 500 baht (threshold included), not member:
    # 500 * 0.95 * 1.07 = 508.25 baht
    assert cafe_bill([{"price": 25_000, "qty": 2}], False) == 50_825
    # Subtotal 500 baht, member: 500 * 0.95 * 0.90 * 1.07 = 457.425 -> 457.43 baht
    assert cafe_bill([{"price": 25_000, "qty": 2}], True) == 45_743
    # Mixed items, member, above threshold: subtotal 846.91 baht
    # 84,691 * 0.95 * 0.90 * 1.07 = 77,479.56135 -> 77,480 satang
    items = [{"price": 12_345, "qty": 2}, {"price": 60_000, "qty": 1}, {"price": 1, "qty": 1}]
    assert cafe_bill(items, True) == 77_480
    print("all checks passed")
