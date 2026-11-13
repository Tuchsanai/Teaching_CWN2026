"""BaanKafe bulk coffee-bean pricing.

All money is in satang (1 baht = 100 satang), so unit_price is an int.
Rates are handled as exact Fractions and the final total is rounded
half-up to a whole satang, so no float error creeps in.
"""

from fractions import Fraction
from math import floor

VAT_RATE = Fraction(7, 100)
COUPON_RATE = Fraction(25, 1000)  # 2.5%
BULK_RATE_50 = Fraction(75, 1000)  # 7.5%, qty >= 50
BULK_RATE_10 = Fraction(35, 1000)  # 3.5%, qty >= 10


def _bulk_rate(qty: int) -> Fraction:
    """Single bulk-tier rate: the highest tier reached applies (not stacked)."""
    if qty >= 50:
        return BULK_RATE_50
    if qty >= 10:
        return BULK_RATE_10
    return Fraction(0)


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
    """Return the amount the customer pays, in whole satang.

    unit_price: price per bag in satang (>= 0)
    qty:        number of bags (1..1000)
    coupon:     True if a coupon is applied (extra 2.5% off)

    Order of calculation:
      1. subtotal = unit_price * qty
      2. bulk discount (3.5% at 10+ bags, 7.5% at 50+ bags)
      3. coupon discount (2.5%), applied to the already-discounted amount
      4. VAT 7% added last
      5. round half-up to an integer number of satang
    """
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise TypeError("unit_price must be an int (satang)")
    if unit_price < 0:
        raise ValueError("unit_price must be >= 0")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise TypeError("qty must be an int")
    if not 1 <= qty <= 1000:
        raise ValueError("qty must be between 1 and 1000")
    if not isinstance(coupon, bool):
        raise TypeError("coupon must be a bool")

    total = Fraction(unit_price * qty)
    total *= 1 - _bulk_rate(qty)
    if coupon:
        total *= 1 - COUPON_RATE
    total *= 1 + VAT_RATE

    # round half-up to whole satang
    return floor(total + Fraction(1, 2))


if __name__ == "__main__":
    print(bulk_price(10000, 1, False))   # 1 bag, 100.00 baht
    print(bulk_price(10000, 10, False))  # 10 bags, 3.5% off
    print(bulk_price(10000, 50, True))   # 50 bags, 7.5% + coupon 2.5%
