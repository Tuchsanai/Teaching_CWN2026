"""BaanKafe member cashback calculator.

All money is handled as integer satang (1 baht = 100 satang) so the
result is exact. Rates are stored in basis points (1% = 100 bp) to keep
the arithmetic integer-only.
"""

MIN_PURCHASE = 100 * 100        # 100 baht, in satang
MAX_CASHBACK = 200 * 100        # 200 baht cap per bill, in satang
BIRTHDAY_MULTIPLIER = 2

# Cashback rate per tier, in basis points (1.5% = 150 bp)
TIER_RATE_BP = {
    "silver": 150,
    "gold": 250,
    "platinum": 400,
}


def cashback(amount, tier, birthday=False):
    """Return the cashback for one bill, as an integer number of satang.

    amount   -- purchase total in satang (int, >= 0)
    tier     -- "silver", "gold" or "platinum"
    birthday -- True if the purchase is made in the member's birthday month

    Rules:
      * purchases below 100 baht earn nothing
      * the rate depends on the tier (1.5% / 2.5% / 4%)
      * a birthday-month purchase earns double
      * cashback is capped at 200 baht per bill
      * the result is rounded down to a whole satang
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount must be an int (satang)")
    if amount < 0:
        raise ValueError("amount must be >= 0")

    key = str(tier).strip().lower()
    if key not in TIER_RATE_BP:
        raise ValueError(f"unknown tier: {tier!r}")

    if amount < MIN_PURCHASE:
        return 0

    rate_bp = TIER_RATE_BP[key]
    if birthday:
        rate_bp *= BIRTHDAY_MULTIPLIER

    # amount * rate_bp / 10000, floored, all in integers
    earned = amount * rate_bp // 10000
    return min(earned, MAX_CASHBACK)


if __name__ == "__main__":
    # Quick self-check
    assert cashback(9999, "gold") == 0                 # under 100 baht
    assert cashback(10000, "silver") == 150            # 100 baht * 1.5% = 1.50 baht
    assert cashback(10000, "silver", True) == 300      # birthday doubles
    assert cashback(10000, "gold") == 250              # 2.5%
    assert cashback(10000, "platinum") == 400          # 4%
    assert cashback(1000000, "platinum") == 20000      # capped at 200 baht
    assert cashback(1000000, "platinum", True) == 20000
    assert cashback(12345, "silver") == 185            # floor(185.175) satang
    print("all checks passed")
