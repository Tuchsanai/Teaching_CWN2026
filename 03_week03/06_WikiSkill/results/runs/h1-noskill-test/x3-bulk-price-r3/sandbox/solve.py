"""BaanKafe bulk coffee-bean pricing.

All money is in satang (integers). Percentages are applied with exact
fractions and the final amount is rounded half-up to a whole satang.
"""

from fractions import Fraction

BULK_TIER_50 = Fraction(75, 1000)   # 7.5% off when qty >= 50
BULK_TIER_10 = Fraction(35, 1000)   # 3.5% off when qty >= 10 (and < 50)
COUPON_RATE = Fraction(25, 1000)    # 2.5% extra off with a coupon
VAT_RATE = Fraction(7, 100)         # 7% VAT, added last


def _bulk_rate(qty: int) -> Fraction:
    if qty >= 50:
        return BULK_TIER_50
    if qty >= 10:
        return BULK_TIER_10
    return Fraction(0)


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
    """Return the amount the customer pays, in whole satang.

    unit_price: price per bag in satang (integer, >= 0)
    qty:        number of bags (integer, 1..1000)
    coupon:     True if a coupon is applied

    Steps:
      1. subtotal = unit_price * qty
      2. bulk discount (one rate only): 3.5% for >= 10 bags, 7.5% for >= 50 bags
      3. coupon discount 2.5% applied on the already-discounted amount
      4. VAT 7% added last
      5. round half-up to an integer number of satang
    """
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise TypeError("unit_price must be an integer number of satang")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise TypeError("qty must be an integer")
    if unit_price < 0:
        raise ValueError("unit_price must be >= 0")
    if not 1 <= qty <= 1000:
        raise ValueError("qty must be between 1 and 1000")

    amount = Fraction(unit_price * qty)
    amount *= 1 - _bulk_rate(qty)
    if coupon:
        amount *= 1 - COUPON_RATE
    amount *= 1 + VAT_RATE

    return _round_half_up(amount)


def _round_half_up(value: Fraction) -> int:
    """Round a non-negative Fraction to the nearest integer, halves go up."""
    return (2 * value.numerator + value.denominator) // (2 * value.denominator)


if __name__ == "__main__":
    print(bulk_price(10000, 50, True))   # 482503
    print(bulk_price(10000, 1, False))   # 10700
