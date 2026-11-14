"""BaanKafe bulk coffee-bean pricing.

Rules (all rates applied to the amount in satang):
  * qty >= 50          -> 7.5% bulk discount
  * 10 <= qty < 50     -> 3.5% bulk discount
  * only one bulk rate applies (they do not stack)
  * coupon             -> extra 2.5%, applied to the already-discounted amount
  * VAT 7%             -> applied last, on the discounted amount

All arithmetic is done with exact fractions; the final amount is rounded
half-up to a whole number of satang.
"""

from fractions import Fraction

VAT_RATE = Fraction(7, 100)
COUPON_RATE = Fraction(25, 1000)  # 2.5%


def _bulk_rate(qty):
    if qty >= 50:
        return Fraction(75, 1000)  # 7.5%
    if qty >= 10:
        return Fraction(35, 1000)  # 3.5%
    return Fraction(0)


def bulk_price(unit_price, qty, coupon):
    """Return the total amount the customer pays, in whole satang.

    unit_price: price per bag in satang (int, >= 0)
    qty:        number of bags (int, 1..1000)
    coupon:     True if a coupon is applied
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
    amount *= 1 - _bulk_rate(qty)
    if coupon:
        amount *= 1 - COUPON_RATE
    amount *= 1 + VAT_RATE

    # Round half-up to whole satang (amount is non-negative).
    num, den = amount.numerator, amount.denominator
    return (2 * num + den) // (2 * den)


if __name__ == "__main__":
    print(bulk_price(10000, 1, False))   # 100 THB, no discount, +VAT -> 10700
    print(bulk_price(10000, 10, False))  # 3.5% off -> 96500 * 1.07 = 103255
    print(bulk_price(10000, 50, True))   # 7.5% and 2.5% off, +VAT -> 482503
