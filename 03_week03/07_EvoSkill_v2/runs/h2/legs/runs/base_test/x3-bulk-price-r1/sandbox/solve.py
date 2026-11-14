"""BaanKafe bulk coffee-bean pricing.

Calculation order:
    1. Subtotal      = unit_price * qty
    2. Bulk discount = 3.5% if qty >= 10, 7.5% if qty >= 50 (one rate only)
    3. Coupon        = a further 2.5% off the amount after step 2, if coupon is True
    4. VAT           = +7% on the amount after step 3
    5. Round the final amount half-up to a whole satang

All arithmetic uses fractions.Fraction so percentages are exact; rounding happens
once, at the end.
"""

from fractions import Fraction
import math

MIN_QTY = 1
MAX_QTY = 1000

BULK_TIERS = (
    (50, Fraction(75, 1000)),  # 7.5% off for 50 bags or more
    (10, Fraction(35, 1000)),  # 3.5% off for 10 bags or more
)
COUPON_RATE = Fraction(25, 1000)  # 2.5%
VAT_RATE = Fraction(7, 100)       # 7%


def _bulk_rate(qty: int) -> Fraction:
    for min_qty, rate in BULK_TIERS:
        if qty >= min_qty:
            return rate
    return Fraction(0)


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
    """Return the amount the customer pays, in whole satang.

    unit_price: price per bag in satang (integer, >= 0)
    qty:        number of bags (integer, 1 to 1000)
    coupon:     True if a coupon is applied
    """
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise TypeError("unit_price must be an int (satang)")
    if unit_price < 0:
        raise ValueError("unit_price must be >= 0")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise TypeError("qty must be an int")
    if not MIN_QTY <= qty <= MAX_QTY:
        raise ValueError(f"qty must be between {MIN_QTY} and {MAX_QTY}")
    if not isinstance(coupon, bool):
        raise TypeError("coupon must be a bool")

    amount = Fraction(unit_price * qty)
    amount *= 1 - _bulk_rate(qty)
    if coupon:
        amount *= 1 - COUPON_RATE
    amount *= 1 + VAT_RATE

    # Round half-up to the nearest satang (amount is never negative here).
    return math.floor(amount + Fraction(1, 2))


if __name__ == "__main__":
    print(bulk_price(10000, 1, False))   # 10700
    print(bulk_price(10000, 10, True))   # 100674
    print(bulk_price(10000, 50, False))  # 500000 * 0.925 * 1.07 = 494875
