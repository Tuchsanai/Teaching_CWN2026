"""BaanKafe member cashback calculator.

All money is handled in satang (1 baht = 100 satang) as integers so that
results are exact integer satang with no floating-point rounding error.
"""

# Cashback rate in basis points (1 bp = 0.01%), so 1.5% = 150 bp.
TIER_RATE_BP = {
    "silver": 150,    # 1.5%
    "gold": 250,      # 2.5%
    "platinum": 400,  # 4%
}

MIN_PURCHASE = 100 * 100      # 100 baht, in satang
MAX_CASHBACK = 200 * 100      # 200 baht cap per bill, in satang
BIRTHDAY_MULTIPLIER = 2       # double cashback in birthday month
BP_DENOMINATOR = 10_000


def cashback(amount, tier, birthday=False):
    """Return the cashback amount in whole satang.

    amount   -- purchase total in satang (int, >= 0)
    tier     -- "silver", "gold" or "platinum"
    birthday -- True if the purchase is made during the member's birthday month

    Rules:
      * purchases under 100 baht earn nothing
      * tier rate: silver 1.5%, gold 2.5%, platinum 4%
      * birthday month doubles the cashback
      * cashback is capped at 200 baht per bill (applied after doubling)
      * result is floored to whole satang
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount must be an int (satang)")
    if amount < 0:
        raise ValueError("amount must be >= 0")

    key = tier.strip().lower() if isinstance(tier, str) else tier
    if key not in TIER_RATE_BP:
        raise ValueError(f"unknown tier: {tier!r}")

    if amount < MIN_PURCHASE:
        return 0

    multiplier = BIRTHDAY_MULTIPLIER if birthday else 1
    result = amount * TIER_RATE_BP[key] * multiplier // BP_DENOMINATOR
    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    # Quick sanity checks (amounts in satang).
    assert cashback(9_999, "platinum") == 0          # under 100 baht
    assert cashback(10_000, "silver") == 150         # 100 baht * 1.5% = 1.50 baht
    assert cashback(10_000, "gold") == 250           # 2.5%
    assert cashback(10_000, "platinum") == 400       # 4%
    assert cashback(10_000, "silver", True) == 300   # birthday x2
    assert cashback(100_000, "platinum") == 4_000    # 1000 baht * 4% = 40 baht
    assert cashback(1_000_000, "platinum") == 20_000 # 4% = 400 baht -> capped 200
    assert cashback(1_000_000, "platinum", True) == 20_000  # capped even with birthday
    assert cashback(600_000, "gold", True) == 20_000  # 6000*2.5%*2 = 300 -> capped 200
    assert cashback(333, "gold") == 0
    assert cashback(12_345, "silver") == 185         # 12345*150/10000 = 185.17 -> 185
    print("all checks passed")
