"""BaanKafe bulk coffee-bean pricing.

Prices are in satang (1 baht = 100 satang).

Rules:
- Bulk discount (single tier, not stacked):
    qty >= 50  -> 7.5%
    qty >= 10  -> 3.5%
    otherwise  -> 0%
- Coupon: an extra 2.5% off, applied after the bulk discount.
- VAT 7% is added last, on the discounted amount.
- The result is the customer's total in whole satang (half-up rounding,
  applied once at the end; no intermediate rounding).
"""

from fractions import Fraction

MIN_QTY = 1
MAX_QTY = 1000

VAT_RATE = Fraction(7, 100)
COUPON_RATE = Fraction(25, 1000)  # 2.5%


def _bulk_rate(qty: int) -> Fraction:
    if qty >= 50:
        return Fraction(75, 1000)  # 7.5%
    if qty >= 10:
        return Fraction(35, 1000)  # 3.5%
    return Fraction(0)


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
    """Return the total amount the customer pays, in whole satang.

    unit_price: price per bag in satang (integer, >= 0)
    qty:        number of bags (integer, 1..1000)
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

    total = Fraction(unit_price * qty)
    total *= 1 - _bulk_rate(qty)
    if coupon:
        total *= 1 - COUPON_RATE
    total *= 1 + VAT_RATE

    # Round half up to the nearest satang, exactly (no float error).
    return int((total + Fraction(1, 2)) // 1)


if __name__ == "__main__":
    print(bulk_price(10000, 1, False))   # 10000 * 1.07 = 10700
    print(bulk_price(10000, 10, False))  # 100000 * 0.965 * 1.07 = 103255
    print(bulk_price(10000, 50, True))   # 500000 * 0.925 * 0.975 * 1.07 = 482503.125 -> 482503
