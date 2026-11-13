"""BaanKafe bulk coffee-bean price calculator.

All money is handled as integer satang to avoid floating-point drift.
Rates are expressed in basis points (1 bp = 0.01%), so 3.5% = 350 bp.

Rules
-----
* qty >= 50  -> 7.5% off (single volume rate, replaces the 10+ rate)
* qty >= 10  -> 3.5% off
* coupon     -> a further 2.5% off, applied to the already-discounted amount
* VAT 7% is added last
* The final amount is rounded half-up to a whole satang.
"""

from decimal import Decimal, ROUND_HALF_UP

BPS_DENOM = 10_000  # 100% in basis points

VOLUME_TIERS = (  # (minimum qty, discount in bp), checked highest first
    (50, 750),  # 7.5%
    (10, 350),  # 3.5%
)
COUPON_BP = 250  # 2.5%
VAT_BP = 700     # 7%

MIN_QTY = 1
MAX_QTY = 1_000


def _volume_discount_bp(qty: int) -> int:
    for min_qty, rate_bp in VOLUME_TIERS:
        if qty >= min_qty:
            return rate_bp
    return 0


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
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
    if not MIN_QTY <= qty <= MAX_QTY:
        raise ValueError(f"qty must be between {MIN_QTY} and {MAX_QTY}")

    subtotal = unit_price * qty  # satang, exact integer

    # Sequential factors, each (BPS_DENOM - rate) / BPS_DENOM.
    volume_factor = BPS_DENOM - _volume_discount_bp(qty)
    coupon_factor = BPS_DENOM - (COUPON_BP if coupon else 0)
    vat_factor = BPS_DENOM + VAT_BP

    # Exact value = subtotal * f1 * f2 * f3 / BPS_DENOM**3 ; round half-up.
    numerator = subtotal * volume_factor * coupon_factor * vat_factor
    divisor = BPS_DENOM ** 3
    total = (numerator + divisor // 2) // divisor
    return total


def _reference(unit_price: int, qty: int, coupon: bool) -> int:
    """Independent Decimal implementation used only for self-checks."""
    d = Decimal(unit_price) * qty
    if qty >= 50:
        d *= Decimal("0.925")
    elif qty >= 10:
        d *= Decimal("0.965")
    if coupon:
        d *= Decimal("0.975")
    d *= Decimal("1.07")
    return int(d.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


if __name__ == "__main__":
    import random

    assert bulk_price(10000, 1, False) == 10700          # 100 baht x 1 bag + VAT
    assert bulk_price(0, 1000, True) == 0
    assert bulk_price(10000, 9, True) == _reference(10000, 9, True)

    rng = random.Random(0)
    for _ in range(20000):
        p = rng.randint(0, 500_000)
        q = rng.randint(MIN_QTY, MAX_QTY)
        c = rng.random() < 0.5
        assert bulk_price(p, q, c) == _reference(p, q, c), (p, q, c)

    for bad in [(-1, 1, False), (100, 0, False), (100, 1001, False)]:
        try:
            bulk_price(*bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {bad}")

    print("bulk_price(10000, 1, False)  =", bulk_price(10000, 1, False))
    print("bulk_price(10000, 10, False) =", bulk_price(10000, 10, False))
    print("bulk_price(10000, 50, True)  =", bulk_price(10000, 50, True))
    print("All checks passed.")
