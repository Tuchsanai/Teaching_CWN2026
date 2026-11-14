RATES_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}  # 1.5%, 2.5%, 4%
MIN_AMOUNT = 100 * 100   # 100 baht in satang
MAX_CASHBACK = 200 * 100  # 200 baht in satang


def cashback(amount, tier, birthday):
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES_PER_MILLE[tier]
    if birthday:
        rate *= 2
    # integer math avoids float errors; fractional satang rounded down
    return min(amount * rate // 1000, MAX_CASHBACK)
