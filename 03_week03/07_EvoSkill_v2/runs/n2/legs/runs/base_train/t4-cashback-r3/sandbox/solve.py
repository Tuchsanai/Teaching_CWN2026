RATES_BP = {"silver": 150, "gold": 250, "platinum": 400}  # basis points
MIN_AMOUNT = 10000   # 100 baht in satang
MAX_CASHBACK = 20000  # 200 baht in satang


def cashback(amount, tier, birthday):
    if amount < MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    result = amount * RATES_BP[tier] * mult // 10000  # floor, integer math
    return min(result, MAX_CASHBACK)
