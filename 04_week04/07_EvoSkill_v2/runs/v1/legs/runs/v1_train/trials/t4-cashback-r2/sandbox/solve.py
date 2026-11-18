from fractions import Fraction

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
MIN_AMOUNT = 100 * 100   # สตางค์
CAP = 200 * 100          # สตางค์


def cashback(amount, tier, birthday):
    if type(amount) is not int or amount < 0:
        raise ValueError("amount must be int >= 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("invalid tier")
    if type(birthday) is not bool:
        raise ValueError("birthday must be bool")

    if amount < MIN_AMOUNT:
        return 0
    rate = RATES[tier]
    # นโยบายร้าน: ตัวคูณเดือนเกิดใช้กับ gold/platinum เท่านั้น
    if birthday and tier in ("gold", "platinum"):
        rate *= 2
    value = Fraction(amount) * rate
    return min(int(value // 1), CAP)  # เงินจ่ายออก ปัดลง
