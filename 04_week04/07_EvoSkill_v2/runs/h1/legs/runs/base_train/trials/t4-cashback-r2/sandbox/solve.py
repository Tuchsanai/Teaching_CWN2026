"""BaanKafe member cashback calculator.

Amounts are in satang (1 baht = 100 satang), so all money math is done with
integers and no floating-point rounding issues.
"""

# Cashback rate per tier, in basis points (1 bp = 0.01%).
# silver 1.5% = 150 bp, gold 2.5% = 250 bp, platinum 4% = 400 bp.
TIER_RATE_BP = {
    "silver": 150,
    "gold": 250,
    "platinum": 400,
}

MIN_PURCHASE = 100 * 100      # 100 baht, in satang
MAX_CASHBACK = 200 * 100      # 200 baht per bill, in satang
BASIS_POINTS = 10_000


def cashback(amount: int, tier: str, birthday: bool) -> int:
    """Return the cashback for one bill, in satang.

    amount   -- purchase total in satang (0 or more)
    tier     -- "silver", "gold" or "platinum"
    birthday -- True if the purchase is made in the member's birthday month

    Rules:
      * purchases under 100 baht earn no cashback
      * base cashback = amount * tier rate (rounded down to whole satang)
      * birthday month doubles the cashback
      * cashback is capped at 200 baht per bill
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount must be an integer number of satang")
    if amount < 0:
        raise ValueError("amount must be 0 or more")

    key = tier.strip().lower() if isinstance(tier, str) else tier
    if key not in TIER_RATE_BP:
        raise ValueError(f"unknown tier: {tier!r}")

    if amount < MIN_PURCHASE:
        return 0

    result = amount * TIER_RATE_BP[key] // BASIS_POINTS
    if birthday:
        result *= 2
    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    # Quick self-check with a few examples.
    examples = [
        (9_999, "gold", False),    # under 100 baht -> 0
        (10_000, "silver", False), # 100 baht * 1.5% = 1.50 baht = 150
        (10_000, "gold", False),   # 100 baht * 2.5% = 250
        (10_000, "platinum", True),# 100 baht * 4% * 2 = 800
        (1_000_000, "platinum", False),  # 10,000 baht * 4% = 400 -> capped 200 baht
        (1_000_000, "silver", True),     # 10,000 baht * 1.5% * 2 = 300 -> capped 200 baht
        (5_000, "gold", True),     # under 100 baht -> 0
    ]
    for amt, tier, bday in examples:
        print(f"amount={amt:>9} tier={tier:<8} birthday={bday!s:<5} -> cashback={cashback(amt, tier, bday)}")
