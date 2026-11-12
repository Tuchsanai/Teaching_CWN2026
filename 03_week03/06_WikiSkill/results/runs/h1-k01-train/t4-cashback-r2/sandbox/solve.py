"""BaanKafe member cashback calculator.

Amounts are in satang (1 baht = 100 satang). All arithmetic is done in
integers, so the result is always an exact whole number of satang.
"""

# Cashback rate per tier, in basis points (1 bp = 0.01%).
# silver 1.5% = 150 bp, gold 2.5% = 250 bp, platinum 4% = 400 bp.
_RATE_BP = {
    "silver": 150,
    "gold": 250,
    "platinum": 400,
}

MIN_AMOUNT = 100 * 100        # 100 baht; smaller bills earn nothing
MAX_CASHBACK = 200 * 100      # 200 baht cap per bill
BIRTHDAY_MULTIPLIER = 2       # purchase made in the member's birthday month
BP_DENOMINATOR = 10_000


def cashback(amount: int, tier: str, birthday: bool = False) -> int:
    """Return the cashback in satang for one bill.

    amount   -- purchase total in satang (int, >= 0)
    tier     -- "silver", "gold" or "platinum"
    birthday -- True if the purchase is in the member's birthday month

    Rules:
      * bills below 100 baht earn 0
      * base rate by tier (1.5% / 2.5% / 4%), floored to whole satang
      * birthday month doubles the cashback
      * the result is capped at 200 baht per bill
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount must be an integer number of satang")
    if amount < 0:
        raise ValueError("amount must be >= 0")

    key = tier.strip().lower() if isinstance(tier, str) else tier
    if key not in _RATE_BP:
        raise ValueError(f"unknown tier: {tier!r}")

    if amount < MIN_AMOUNT:
        return 0

    result = amount * _RATE_BP[key] // BP_DENOMINATOR
    if birthday:
        result *= BIRTHDAY_MULTIPLIER
    return min(result, MAX_CASHBACK)
