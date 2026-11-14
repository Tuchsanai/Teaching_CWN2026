"""BaanKafe bulk coffee-bean pricing.

All money is handled as integer satang and all rates as integer permille
(1/1000) or percent, so no floating-point error creeps into the result.
"""

# Volume tiers (qty threshold, discount in permille). Only one tier applies.
VOLUME_TIERS = (
    (50, 75),  # 7.5%
    (10, 35),  # 3.5%
    (1, 0),
)
COUPON_PERMILLE = 25   # 2.5%, added to the volume discount when a coupon is used
VAT_PERCENT = 7        # 7%, applied last


def _round_half_up(numerator, denominator):
    """Integer division rounding half up (for non-negative values)."""
    return (numerator + denominator // 2) // denominator


def bulk_price(unit_price, qty, coupon):
    """Return the amount the customer pays, in whole satang.

    unit_price -- price per bag in satang (int >= 0)
    qty        -- number of bags (int, 1..1000)
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

    gross = unit_price * qty  # satang, exact

    # Volume discount: the single highest tier reached (not stacked).
    volume = next(rate for threshold, rate in VOLUME_TIERS if qty >= threshold)
    discount = volume + (COUPON_PERMILLE if coupon else 0)  # permille

    # Subtotal after discount, rounded to whole satang.
    after_discount = _round_half_up(gross * (1000 - discount), 1000)

    # VAT 7% on top, rounded to whole satang.
    total = _round_half_up(after_discount * (100 + VAT_PERCENT), 100)
    return total


if __name__ == "__main__":
    # Quick self-check (values worked out by hand).
    assert bulk_price(10000, 1, False) == 10700    # 100.00 + VAT 7%
    assert bulk_price(10000, 10, False) == 103255  # 1000.00 -3.5% = 965.00 +VAT
    assert bulk_price(10000, 10, True) == 100580   # 1000.00 -6% = 940.00 +VAT
    assert bulk_price(10000, 50, False) == 494875  # 5000.00 -7.5% = 4625.00 +VAT
    assert bulk_price(10000, 50, True) == 481500   # 5000.00 -10% = 4500.00 +VAT
    print("all checks passed")
