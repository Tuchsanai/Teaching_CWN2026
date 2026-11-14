RATES_PER_MILLE = {"silver": 15, "gold": 25, "platinum": 40}
MIN_AMOUNT = 10000   # 100 baht in satang
MAX_CASHBACK = 20000  # 200 baht in satang


def cashback(amount, tier, birthday):
    if amount < MIN_AMOUNT:
        return 0
    rate = RATES_PER_MILLE[tier]
    if birthday:
        rate *= 2
    # integer math avoids float error; floor to whole satang
    result = amount * rate // 1000
    return min(result, MAX_CASHBACK)
