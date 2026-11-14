"""BaanKafe bulk coffee-bean pricing.

bulk_price(unit_price, qty, coupon) -> int

- unit_price: price per bag in satang (>= 0)
- qty: number of bags (1..1000)
- coupon: True if the customer has a coupon

Rules:
- qty >= 50  -> 7.5% off (single tier, not stacked)
- qty >= 10  -> 3.5% off
- coupon     -> a further 2.5% off, applied after the tier discount
- VAT 7% is added last
- Returns the amount the customer pays, in whole satang (rounded half up).

All math uses integers in basis points (1 bp = 0.01%) so there are no
floating-point errors.
"""

# Basis points: 10000 bp = 100%
_TIER_RULES = ((50, 750), (10, 350))  # (min qty, discount bp), highest tier first
_COUPON_BP = 250
_VAT_BP = 700
_BP_FULL = 10_000


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def bulk_price(unit_price, qty, coupon=False):
    if not _is_int(unit_price) or unit_price < 0:
        raise ValueError("unit_price must be a non-negative integer (satang)")
    if not _is_int(qty) or not 1 <= qty <= 1000:
        raise ValueError("qty must be an integer in 1..1000")
    if not isinstance(coupon, bool):
        raise ValueError("coupon must be a bool")

    tier_bp = 0
    for min_qty, bp in _TIER_RULES:
        if qty >= min_qty:
            tier_bp = bp
            break

    coupon_bp = _COUPON_BP if coupon else 0

    subtotal = unit_price * qty
    numerator = (
        subtotal
        * (_BP_FULL - tier_bp)
        * (_BP_FULL - coupon_bp)
        * (_BP_FULL + _VAT_BP)
    )
    denominator = _BP_FULL ** 3

    # Integer division with round-half-up to the nearest satang
    quotient, remainder = divmod(numerator, denominator)
    if 2 * remainder >= denominator:
        quotient += 1
    return quotient


if __name__ == "__main__":
    cases = [
        (10000, 1, False),   # 100.00 THB, no discount -> 107.00
        (10000, 10, False),  # 3.5% off
        (10000, 49, True),   # 3.5% + coupon
        (10000, 50, False),  # 7.5% off
        (10000, 50, True),   # 7.5% + coupon
        (0, 1000, True),
        (12345, 7, True),
    ]
    for unit, qty, cpn in cases:
        print(unit, qty, cpn, "->", bulk_price(unit, qty, cpn))
