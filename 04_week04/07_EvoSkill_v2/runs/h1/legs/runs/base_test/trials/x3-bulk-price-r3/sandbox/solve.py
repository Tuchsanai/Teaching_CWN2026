"""BaanKafe bulk coffee-bean pricing.

All money is in satang (integer). Discounts are applied in sequence
(bulk tier, then coupon), VAT 7% is applied last, and the result is
rounded once to a whole satang (half-up).
"""

from decimal import Decimal, ROUND_HALF_UP


def _bulk_rate(qty: int) -> Decimal:
    if qty >= 50:
        return Decimal("0.075")
    if qty >= 10:
        return Decimal("0.035")
    return Decimal("0")


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
    """Return the total amount the customer pays, in whole satang.

    unit_price: price per bag in satang (>= 0)
    qty:        number of bags (1..1000)
    coupon:     True if a coupon is applied (extra 2.5% off)
    """
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise TypeError("unit_price must be an int (satang)")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise TypeError("qty must be an int")
    if unit_price < 0:
        raise ValueError("unit_price must be >= 0")
    if not 1 <= qty <= 1000:
        raise ValueError("qty must be between 1 and 1000")

    total = Decimal(unit_price) * Decimal(qty)
    total *= Decimal("1") - _bulk_rate(qty)
    if coupon:
        total *= Decimal("1") - Decimal("0.025")
    total *= Decimal("1.07")  # VAT 7%, applied last

    return int(total.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


if __name__ == "__main__":
    print(bulk_price(10000, 1, False))   # 10700
    print(bulk_price(10000, 10, False))  # 103255
    print(bulk_price(10000, 50, True))   # 482503
