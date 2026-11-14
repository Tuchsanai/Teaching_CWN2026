"""BaanKafe bulk coffee-bean pricing.

All money is in satang (1 baht = 100 satang).

Rules applied in order:
  1. Volume discount (single rate, not stacked):
       qty >= 50  -> 7.5 %
       qty >= 10  -> 3.5 %
       otherwise  -> 0 %
  2. Coupon: an extra 2.5 % off the already-discounted amount (applied
     sequentially, so the coupon is taken off the volume-discounted price).
  3. VAT 7 % added last.

Arithmetic uses exact fractions; the final amount is rounded once,
half-up, to a whole satang.
"""

from fractions import Fraction
from decimal import Decimal, ROUND_HALF_UP

VOLUME_TIERS = (  # (minimum quantity, discount rate), highest tier first
    (50, Fraction(75, 1000)),
    (10, Fraction(35, 1000)),
)
COUPON_RATE = Fraction(25, 1000)
VAT_RATE = Fraction(7, 100)


def _volume_rate(qty: int) -> Fraction:
    for min_qty, rate in VOLUME_TIERS:
        if qty >= min_qty:
            return rate
    return Fraction(0)


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
    """Return the total amount the customer pays, in whole satang.

    unit_price -- price per bag in satang (integer, >= 0)
    qty        -- number of bags (integer, 1..1000)
    coupon     -- True if a coupon is applied
    """
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise TypeError("unit_price must be an int (satang)")
    if unit_price < 0:
        raise ValueError("unit_price must be >= 0")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise TypeError("qty must be an int")
    if not 1 <= qty <= 1000:
        raise ValueError("qty must be between 1 and 1000")

    amount = Fraction(unit_price * qty)
    amount *= 1 - _volume_rate(qty)
    if coupon:
        amount *= 1 - COUPON_RATE
    amount *= 1 + VAT_RATE

    # Round half-up to a whole satang, done once at the end.
    rounded = Decimal(amount.numerator) / Decimal(amount.denominator)
    return int(rounded.quantize(Decimal(1), rounding=ROUND_HALF_UP))


if __name__ == "__main__":
    # Sanity checks (unit price 100 baht = 10000 satang).
    assert bulk_price(10000, 1, False) == 10700      # 10000 * 1.07
    assert bulk_price(10000, 9, False) == 9 * 10000 * 107 // 100  # no volume discount below 10
    assert bulk_price(10000, 10, False) == 103255    # 100000 * 0.965 * 1.07
    assert bulk_price(10000, 50, False) == 494875    # 500000 * 0.925 * 1.07
    assert bulk_price(10000, 50, True) == 482503     # 462500 * 0.975 * 1.07 = 482503.125 -> 482503
    assert bulk_price(0, 1000, True) == 0
    print("ok")
    print(bulk_price(10000, 1, False), bulk_price(10000, 10, False),
          bulk_price(10000, 50, True), bulk_price(10000, 1000, True))
