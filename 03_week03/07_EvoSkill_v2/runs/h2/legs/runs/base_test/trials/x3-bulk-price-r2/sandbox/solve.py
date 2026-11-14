"""BaanKafe bulk coffee-bean pricing.

All money is in satang (1 baht = 100 satang). Intermediate math uses Decimal
so there is no floating-point drift; only the final amount is rounded, to a
whole satang (half-up).
"""

from decimal import Decimal, ROUND_HALF_UP

VAT_RATE = Decimal("0.07")
BULK_TIER_50 = (50, Decimal("0.075"))  # 50 bags or more: 7.5% off
BULK_TIER_10 = (10, Decimal("0.035"))  # 10 bags or more: 3.5% off
COUPON_RATE = Decimal("0.025")         # extra 2.5% off with a coupon
MAX_QTY = 1000


def _bulk_rate(qty: int) -> Decimal:
    """Return the single bulk-discount rate that applies to qty (highest tier wins)."""
    if qty >= BULK_TIER_50[0]:
        return BULK_TIER_50[1]
    if qty >= BULK_TIER_10[0]:
        return BULK_TIER_10[1]
    return Decimal("0")


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
    """Return the total amount the customer pays, in whole satang.

    unit_price -- price per bag in satang (int, >= 0)
    qty        -- number of bags (int, 1..1000)
    coupon     -- True if a coupon is applied

    Order of calculation:
      1. subtotal = unit_price * qty
      2. bulk discount (3.5% for >= 10 bags, 7.5% for >= 50 bags; one rate only)
      3. coupon discount 2.5%, applied on the already-discounted amount
      4. VAT 7% added last
    """
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise TypeError("unit_price must be an int (satang)")
    if unit_price < 0:
        raise ValueError("unit_price must be >= 0")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise TypeError("qty must be an int")
    if not 1 <= qty <= MAX_QTY:
        raise ValueError(f"qty must be between 1 and {MAX_QTY}")

    amount = Decimal(unit_price) * Decimal(qty)
    amount *= Decimal("1") - _bulk_rate(qty)
    if coupon:
        amount *= Decimal("1") - COUPON_RATE
    amount *= Decimal("1") + VAT_RATE

    return int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


if __name__ == "__main__":
    # Quick examples (prices in satang).
    print(bulk_price(25000, 1, False))   # 1 bag, no coupon   -> 26750
    print(bulk_price(25000, 10, False))  # 10 bags (3.5% off) -> 258138
    print(bulk_price(25000, 50, True))   # 50 bags + coupon
    print(bulk_price(25000, 1000, True))
