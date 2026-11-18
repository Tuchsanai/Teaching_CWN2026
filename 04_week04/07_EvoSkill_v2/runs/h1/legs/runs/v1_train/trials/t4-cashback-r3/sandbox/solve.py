from fractions import Fraction

MIN_AMOUNT = 10_000     # 100 บาท (สตางค์) ต่ำกว่านี้ไม่ได้เงินคืน
MAX_CASHBACK = 20_000   # 200 บาท (สตางค์) เพดานต่อบิล
BIRTHDAY_MULTIPLIER = 2

RATES = {
    "silver": Fraction(15, 1000),   # 1.5%
    "gold": Fraction(25, 1000),     # 2.5%
    "platinum": Fraction(4, 100),   # 4%
}


def _require_int(value, name):
    if type(value) is not int:          # ปฏิเสธ bool, float, str, None
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if value < 0:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า 0")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int, x ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def cashback(amount, tier, birthday):
    """คืนเงินคืนสมาชิกเป็นสตางค์ (int)

    amount   : ยอดซื้อเป็นสตางค์ (int, >= 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด (ได้เงินคืน 2 เท่า)
    """
    _require_int(amount, "amount")
    if type(tier) is not str or tier not in RATES:
        raise ValueError(f"tier ต้องเป็นหนึ่งใน {sorted(RATES)}")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    if amount < MIN_AMOUNT:
        return 0

    multiplier = BIRTHDAY_MULTIPLIER if birthday else 1
    raw = Fraction(amount) * RATES[tier] * multiplier   # คูณทุกตัวก่อน ยังไม่ปัด
    return min(_half_up(raw), MAX_CASHBACK)              # ปัดครั้งเดียว แล้วคิดเพดาน


if __name__ == "__main__":
    print(cashback(10_000, "silver", False))   # 150
    print(cashback(10_000, "gold", True))      # 500
    print(cashback(600_000, "platinum", True)) # 20000
