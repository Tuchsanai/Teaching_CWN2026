"""BaanKafe cashback (หน่วยสตางค์)"""
from fractions import Fraction

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
MIN_AMOUNT = 10000   # 100 บาท
CAP = 20000          # 200 บาท


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount ต้องเป็นจำนวนเต็มตั้งแต่ 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ต้องเป็น silver, gold หรือ platinum")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")
    if amount < MIN_AMOUNT:
        return 0
    x = Fraction(amount) * RATES[tier]
    if birthday:
        x *= 2
    x = min(x, Fraction(CAP))
    return int(x // 1)
