from fractions import Fraction

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
MIN_AMOUNT = 100 * 100   # 100 บาท เป็นสตางค์
CAP = 200 * 100          # 200 บาท เป็นสตางค์


def cashback(amount, tier, birthday):
    # ตรวจอินพุตก่อนทุกอย่าง
    if type(amount) is not int or amount < 0:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม >= 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ไม่ถูกต้อง")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True/False")

    if amount < MIN_AMOUNT:
        return 0
    value = amount * RATES[tier] * (2 if birthday else 1)
    # เงินที่ร้านจ่ายออก -> ปัดลง แล้วค่อยใช้เพดาน
    return min(CAP, value.numerator // value.denominator)
