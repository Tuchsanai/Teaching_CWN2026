RATE_BP = {"silver": 150, "gold": 250, "platinum": 400}  # basis points
MIN_AMOUNT = 100_00  # 100 baht in satang
CAP = 200_00         # 200 baht in satang


def cashback(amount, tier, birthday):
    if amount < MIN_AMOUNT:
        return 0
    bp = RATE_BP[tier]
    if birthday:
        bp *= 2
    # integer math avoids float error; fractional satang is floored
    return min(amount * bp // 10_000, CAP)
