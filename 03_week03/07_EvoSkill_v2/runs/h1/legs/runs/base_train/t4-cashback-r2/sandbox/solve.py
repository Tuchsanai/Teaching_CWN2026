"""BaanKafe cashback calculator.

cashback(amount, tier, birthday) -> cashback amount in satang (integer).

Rules:
- amount: purchase total in satang (integer, >= 0). 100 baht = 10000 satang.
- tier: "silver" (1.5%), "gold" (2.5%), "platinum" (4%).
- birthday: True if the purchase is in the member's birthday month -> cashback x2.
- Purchases below 100 baht earn no cashback.
- Cashback is capped at 200 baht (20000 satang) per bill.
- Result is an integer number of satang, rounded down (truncated).
"""

# Rates as exact fractions (numerator, denominator) to avoid float error.
TIER_RATES = {
    "silver": (3, 200),    # 1.5%
    "gold": (1, 40),       # 2.5%
    "platinum": (1, 25),   # 4%
}

MIN_PURCHASE = 100 * 100      # 100 baht in satang
MAX_CASHBACK = 200 * 100      # 200 baht in satang
BIRTHDAY_MULTIPLIER = 2


def cashback(amount, tier, birthday=False):
    """Return the cashback in satang for one bill."""
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount must be an integer number of satang")
    if amount < 0:
        raise ValueError("amount must be >= 0")

    key = tier.strip().lower() if isinstance(tier, str) else tier
    if key not in TIER_RATES:
        raise ValueError(f"unknown tier: {tier!r}")

    if amount < MIN_PURCHASE:
        return 0

    num, den = TIER_RATES[key]
    multiplier = BIRTHDAY_MULTIPLIER if birthday else 1

    result = amount * num * multiplier // den
    return min(result, MAX_CASHBACK)
