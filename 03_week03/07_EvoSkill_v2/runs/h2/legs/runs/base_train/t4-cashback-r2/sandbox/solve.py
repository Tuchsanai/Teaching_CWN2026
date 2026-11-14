"""BaanKafe cashback calculator.

cashback(amount, tier, birthday) -> int (satang)

- amount   : purchase total in satang (>= 0)
- tier     : "silver" | "gold" | "platinum"
- birthday : True if the purchase is in the member's birthday month

Rules:
- Rates: silver 1.5%, gold 2.5%, platinum 4%
- Purchases under 100 baht (10,000 satang) earn no cashback.
- Birthday month doubles the cashback.
- Cashback is capped at 200 baht (20,000 satang) per bill.
- Result is an integer number of satang (rounded half up).

Rates are kept in basis points (1 bp = 0.01%) so the arithmetic stays exact
with integers and avoids float rounding errors.
"""

MIN_AMOUNT_SATANG = 10_000      # 100 baht
MAX_CASHBACK_SATANG = 20_000    # 200 baht per bill
BIRTHDAY_MULTIPLIER = 2

RATE_BP = {
    "silver": 150,    # 1.5%
    "gold": 250,      # 2.5%
    "platinum": 400,  # 4%
}


def cashback(amount: int, tier: str, birthday: bool) -> int:
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount must be an int (satang)")
    if amount < 0:
        raise ValueError("amount must be >= 0")

    key = str(tier).strip().lower()
    if key not in RATE_BP:
        raise ValueError(f"unknown tier: {tier!r}")

    if amount < MIN_AMOUNT_SATANG:
        return 0

    multiplier = BIRTHDAY_MULTIPLIER if birthday else 1

    # amount * rate_bp / 10000, rounded half up, using integer math only
    numerator = amount * RATE_BP[key] * multiplier
    value = (numerator + 5_000) // 10_000

    return min(value, MAX_CASHBACK_SATANG)


if __name__ == "__main__":
    # Quick self-check
    assert cashback(9_999, "platinum", True) == 0        # under 100 baht
    assert cashback(10_000, "silver", False) == 150      # 100 baht * 1.5%
    assert cashback(10_000, "gold", False) == 250
    assert cashback(10_000, "platinum", False) == 400
    assert cashback(10_000, "silver", True) == 300       # birthday x2
    assert cashback(100_000, "gold", False) == 2_500     # 1000 baht * 2.5%
    assert cashback(1_000_000, "platinum", False) == 20_000  # capped at 200 baht
    assert cashback(1_000_000, "silver", True) == 20_000     # 30,000 capped
    assert cashback(5_000, "gold", True) == 0            # under 100 baht
    assert cashback(12_345, "silver", False) == 185      # 185.175 -> 185
    print("all checks passed")
