RATES_PERMILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 100 * 100   # 100 baht in satang
MAX_CASHBACK = 200 * 100  # 200 baht in satang


def cashback(amount, tier, birthday):
    """Return cashback in whole satang (amount is in satang)."""
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES_PERMILLE[tier]
    if birthday:
        rate *= 2
    # integer math avoids float error; fractions of a satang are floored
    result = amount * rate // 1000
    return min(result, MAX_CASHBACK)
