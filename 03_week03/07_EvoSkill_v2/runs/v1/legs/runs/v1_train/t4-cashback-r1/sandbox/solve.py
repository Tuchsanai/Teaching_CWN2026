from fractions import Fraction

RATES = {"silver": Fraction(15, 1000), "gold": Fraction(25, 1000), "platinum": Fraction(4, 100)}
MIN_AMOUNT = 10000   # 100 บาท (สตางค์)
CAP = 20000          # 200 บาท (สตางค์)
# สมมติฐาน (brief เงียบ): โบนัสเดือนเกิด x2 ให้เฉพาะ gold/platinum ไม่รวม silver
BIRTHDAY_TIERS = {"gold", "platinum"}


def need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def need_bool(v, name):
    if type(v) is not bool:
        raise ValueError(f"{name} ต้องเป็น True/False")
    return v


def cashback(amount, tier, birthday):
    need_int(amount, "amount", low=0)
    if type(tier) is not str or tier not in RATES:
        raise ValueError("tier ไม่ถูกต้อง")
    need_bool(birthday, "birthday")

    if amount < MIN_AMOUNT:
        return 0
    rate = RATES[tier]
    if birthday and tier in BIRTHDAY_TIERS:
        rate *= 2
    value = (amount * rate.numerator) // rate.denominator  # ปัดลง (เงินที่ร้านจ่ายออก)
    return min(CAP, value)
