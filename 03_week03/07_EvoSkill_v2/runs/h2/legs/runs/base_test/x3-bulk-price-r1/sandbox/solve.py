"""BaanKafe bulk coffee-bean pricing.

All money is handled in satang (1 baht = 100 satang) and computed with exact
fractions, so the result is never affected by floating-point error.

Rules:
  * Volume discount (only one tier applies):
      qty >= 50 -> 7.5 %
      qty >= 10 -> 3.5 %
      otherwise -> 0 %
  * Coupon (optional): a further 2.5 % off the already-discounted amount.
  * VAT 7 % is added last, on the final amount.
  * The result is rounded half-up to a whole satang.
"""

from fractions import Fraction
from math import floor

MIN_QTY = 1
MAX_QTY = 1000

VOLUME_TIERS = (
    (50, Fraction(75, 1000)),  # 7.5 %
    (10, Fraction(35, 1000)),  # 3.5 %
)
COUPON_RATE = Fraction(25, 1000)  # 2.5 %
VAT_RATE = Fraction(7, 100)       # 7 %


def _volume_rate(qty: int) -> Fraction:
    for min_qty, rate in VOLUME_TIERS:
        if qty >= min_qty:
            return rate
    return Fraction(0)


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
    """Return the total amount the customer pays, in whole satang.

    unit_price -- price per bag in satang (integer, >= 0)
    qty        -- number of bags (1..1000)
    coupon     -- True if a coupon is applied
    """
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise TypeError("unit_price must be an int (satang)")
    if unit_price < 0:
        raise ValueError("unit_price must be >= 0")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise TypeError("qty must be an int")
    if not MIN_QTY <= qty <= MAX_QTY:
        raise ValueError(f"qty must be between {MIN_QTY} and {MAX_QTY}")

    amount = Fraction(unit_price * qty)
    amount *= 1 - _volume_rate(qty)
    if coupon:
        amount *= 1 - COUPON_RATE
    amount *= 1 + VAT_RATE

    # Round half-up to the nearest whole satang.
    return floor(amount + Fraction(1, 2))


if __name__ == "__main__":
    print(bulk_price(10000, 1, False))   # 100 baht x 1, no discount -> 10700
    print(bulk_price(10000, 10, False))  # 3.5 % off -> 103255
    print(bulk_price(10000, 50, True))   # 7.5 % + coupon 2.5 %, + VAT
