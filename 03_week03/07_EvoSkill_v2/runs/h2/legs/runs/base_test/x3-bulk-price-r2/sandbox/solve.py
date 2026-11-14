"""BaanKafe bulk coffee-bean pricing.

All money is in satang (1 baht = 100 satang), so every input and output
amount is an integer number of satang.
"""

from decimal import Decimal, ROUND_HALF_UP

VAT_RATE = Decimal("0.07")
COUPON_RATE = Decimal("0.025")


def _volume_rate(qty: int) -> Decimal:
    """Return the single volume-discount rate that applies to ``qty`` bags."""
    if qty >= 50:
        return Decimal("0.075")
    if qty >= 10:
        return Decimal("0.035")
    return Decimal("0")


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
    """Return the total amount the customer pays, in satang.

    Steps:
      1. subtotal = unit_price * qty
      2. volume discount: 3.5% for qty >= 10, 7.5% for qty >= 50 (one rate only)
      3. coupon: an extra 2.5% off the discounted amount, if ``coupon`` is True
      4. VAT 7% added last
      5. round half-up to whole satang

    Raises ValueError for out-of-range inputs.
    """
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise ValueError("unit_price must be an integer number of satang")
    if unit_price < 0:
        raise ValueError("unit_price must be >= 0")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise ValueError("qty must be an integer")
    if not 1 <= qty <= 1000:
        raise ValueError("qty must be between 1 and 1000")
    if not isinstance(coupon, bool):
        raise ValueError("coupon must be True or False")

    amount = Decimal(unit_price) * Decimal(qty)
    amount *= Decimal(1) - _volume_rate(qty)
    if coupon:
        amount *= Decimal(1) - COUPON_RATE
    amount *= Decimal(1) + VAT_RATE

    return int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
