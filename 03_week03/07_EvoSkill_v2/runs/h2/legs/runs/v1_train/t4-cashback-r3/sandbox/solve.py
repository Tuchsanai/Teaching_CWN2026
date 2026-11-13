"""BaanKafe cashback calculator.

Units: amount is in satang (1 baht = 100 satang). Result is integer satang.

Rules, applied in order:
1. amount below 100 baht (10,000 satang) -> no cashback.
2. Base rate by tier: silver 1.5%, gold 2.5%, platinum 4%.
3. Birthday purchase (birthday=True) -> cashback doubled.
4. Cap at 200 baht (20,000 satang) per bill, applied after doubling.
5. Round once, at the end, half-up to whole satang.
"""

import math
from fractions import Fraction

RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(4, 100),    # 4%
}
MIN_AMOUNT = 100 * 100      # 100 baht in satang
MAX_CASHBACK = 200 * 100    # 200 baht in satang


def _round_half_up(f):
    """Round a non-negative Fraction to the nearest integer, halves go up."""
    return math.floor(f + Fraction(1, 2))


def cashback(amount, tier, birthday):
    """Return the cashback in whole satang for one bill.

    amount   -- purchase total in satang (int, >= 0)
    tier     -- "silver", "gold" or "platinum"
    birthday -- True if the purchase is in the member's birthday month
    """
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise TypeError("amount must be a number of satang")
    amt = Fraction(str(amount))  # avoid float binary error
    if amt < 0:
        raise ValueError("amount must not be negative")

    key = tier.strip().lower() if isinstance(tier, str) else None
    if key not in RATES:
        raise ValueError(f"unknown tier: {tier!r}")

    if amt < MIN_AMOUNT:
        return 0

    result = amt * RATES[key]
    if birthday:
        result *= 2
    result = _round_half_up(result)
    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    print(cashback(10000, "silver", False))   # 150 satang = 1.50 baht
    print(cashback(10100, "silver", False))   # 151.5 -> 152
    print(cashback(500000, "platinum", False))  # 20000 (capped)
