"""BaanKafe member cashback calculator.

All money values are in satang (1 baht = 100 satang); the result is an
integer number of satang.
"""

# Rate per tier expressed as parts per 1000 to keep the arithmetic in integers
# (silver 1.5% = 15/1000, gold 2.5% = 25/1000, platinum 4% = 40/1000).
_RATE_PER_MILLE = {
    "silver": 15,
    "gold": 25,
    "platinum": 40,
}

MIN_PURCHASE = 100 * 100     # 100 baht, in satang
MAX_CASHBACK = 200 * 100     # 200 baht per bill, in satang
BIRTHDAY_MULTIPLIER = 2


def cashback(amount: int, tier: str, birthday: bool) -> int:
    """Return the cashback amount in satang for a single bill.

    amount   -- purchase total in satang (>= 0)
    tier     -- "silver", "gold" or "platinum"
    birthday -- True if the purchase is made during the member's birthday month

    Rules:
      * purchases below 100 baht earn no cashback
      * base rate: silver 1.5%, gold 2.5%, platinum 4%
      * birthday month doubles the cashback
      * cashback is capped at 200 baht per bill
      * the result is a whole number of satang (fractions are rounded down)
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount must be an integer number of satang")
    if amount < 0:
        raise ValueError("amount must be >= 0")

    key = tier.strip().lower() if isinstance(tier, str) else tier
    if key not in _RATE_PER_MILLE:
        raise ValueError(f"unknown tier: {tier!r}")

    if amount < MIN_PURCHASE:
        return 0

    result = amount * _RATE_PER_MILLE[key] // 1000
    if birthday:
        result *= BIRTHDAY_MULTIPLIER
    return min(result, MAX_CASHBACK)


if __name__ == "__main__":
    # Quick self-check with sample values (amounts in satang).
    assert cashback(9999, "gold", False) == 0          # under 100 baht
    assert cashback(10000, "silver", False) == 150     # 100 baht * 1.5%
    assert cashback(10000, "silver", True) == 300      # birthday doubles
    assert cashback(10000, "gold", False) == 250       # 100 baht * 2.5%
    assert cashback(10000, "platinum", False) == 400   # 100 baht * 4%
    assert cashback(10001, "silver", False) == 150     # 1.5015 -> rounds down to 150
    assert cashback(1_000_000, "platinum", False) == 20000  # capped at 200 baht
    assert cashback(1_000_000, "silver", True) == 20000     # capped after doubling
    assert cashback(500_000, "platinum", True) == 20000     # 4% * 2 = 8% -> capped
    assert cashback(200_000, "gold", False) == 5000         # 2000 baht * 2.5% = 50 baht
    print("all checks passed")
