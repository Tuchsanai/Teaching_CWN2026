"""BaanKafe bulk coffee-bean pricing.

All money is in satang (integer). Percentages are handled in basis points
(1% = 100 bp) and every step uses exact integer arithmetic, so there is no
floating-point drift. The final total is rounded half-up to whole satang.

Rules:
- qty >= 50  -> 7.5% bulk discount
- qty >= 10  -> 3.5% bulk discount   (only one bulk rate applies)
- coupon     -> further 2.5% off, applied to the already-discounted amount
- VAT 7% is added last, on the amount after discounts.
"""

BULK_TIERS = ((50, 750), (10, 350))  # (min qty, discount in basis points), highest first
COUPON_BP = 250                      # 2.5%
VAT_BP = 700                         # 7%
BP_DENOM = 10_000


def _bulk_bp(qty: int) -> int:
    for min_qty, bp in BULK_TIERS:
        if qty >= min_qty:
            return bp
    return 0


def _div_round_half_up(numerator: int, denominator: int) -> int:
    """Integer division rounding half up (numerator and denominator are > 0)."""
    return (numerator + denominator // 2) // denominator


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
    """Return the total amount the customer pays, in whole satang.

    unit_price: price per bag in satang (>= 0)
    qty:        number of bags (1..1000)
    coupon:     True if a coupon is applied
    """
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise TypeError("unit_price must be an int (satang)")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise TypeError("qty must be an int")
    if unit_price < 0:
        raise ValueError("unit_price must be >= 0")
    if not 1 <= qty <= 1000:
        raise ValueError("qty must be between 1 and 1000")

    subtotal = unit_price * qty  # satang, exact

    # Numerator/denominator kept as integers; final rounding happens once.
    numerator = subtotal * (BP_DENOM - _bulk_bp(qty))
    denominator = BP_DENOM
    if coupon:
        numerator *= BP_DENOM - COUPON_BP
        denominator *= BP_DENOM
    # VAT 7% on the discounted amount
    numerator *= BP_DENOM + VAT_BP
    denominator *= BP_DENOM

    return _div_round_half_up(numerator, denominator)


if __name__ == "__main__":
    # Quick sanity checks
    assert bulk_price(10000, 1, False) == 10700          # 100.00 THB +7% VAT
    assert bulk_price(10000, 9, False) == 9 * 10700      # no bulk discount below 10
    assert bulk_price(10000, 10, False) == 103_255       # 1,000.00 * 0.965 * 1.07
    assert bulk_price(10000, 50, False) == 494_875       # 5,000.00 * 0.925 * 1.07
    assert bulk_price(10000, 50, True) == 482_503        # 5,000.00 * 0.925 * 0.975 * 1.07 = 482,503.125 -> 482,503
    print("bulk_price(10000, 10, False) =", bulk_price(10000, 10, False))
    print("bulk_price(10000, 50, False) =", bulk_price(10000, 50, False))
    print("bulk_price(10000, 50, True)  =", bulk_price(10000, 50, True))
    print("bulk_price(0, 5, True)       =", bulk_price(0, 5, True))
    print("bulk_price(12345, 1000, True)=", bulk_price(12345, 1000, True))
