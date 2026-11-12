RATES_BP = {"silver": 150, "gold": 250, "platinum": 400}  # basis points (1bp = 0.01%)
MIN_AMOUNT = 10000  # 100 baht in satang
CAP = 20000         # 200 baht in satang


def cashback(amount, tier, birthday):
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    # integer math avoids float errors; round down to whole satang
    result = amount * RATES_BP[tier] * mult // 10000
    return min(result, CAP)
