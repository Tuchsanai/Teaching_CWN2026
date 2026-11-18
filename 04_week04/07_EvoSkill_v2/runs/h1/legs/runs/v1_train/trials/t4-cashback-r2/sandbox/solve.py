from fractions import Fraction

# อัตราเงินคืนของแต่ละระดับสมาชิก (เศษส่วน ไม่ใช้ float)
RATES = {
    "silver": Fraction(3, 200),    # 1.5%
    "gold": Fraction(1, 40),       # 2.5%
    "platinum": Fraction(1, 25),   # 4%
}
MIN_PURCHASE = 10_000    # 100 บาท (หน่วยสตางค์)
MAX_CASHBACK = 20_000    # 200 บาทต่อบิล (หน่วยสตางค์)
BIRTHDAY_MULTIPLIER = 2


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int, x ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def cashback(amount, tier, birthday):
    """คืนค่าเงินคืนสมาชิกเป็นจำนวนเต็มสตางค์

    amount   : ยอดซื้อเป็นสตางค์ (int, >= 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด (เงินคืน 2 เท่า)
    """
    # ตรวจ input ทั้งหมดก่อนคำนวณ
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่น้อยกว่า 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError(f"tier ต้องเป็นหนึ่งใน {sorted(RATES)}")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    # ยอดต่ำกว่า 100 บาท ไม่ได้เงินคืน
    if amount < MIN_PURCHASE:
        return 0

    # คูณทุกตัวคูณก่อน แล้วค่อย cap แล้วปัดครั้งเดียวตอนท้าย
    cb = Fraction(amount) * RATES[tier]
    if birthday:
        cb *= BIRTHDAY_MULTIPLIER
    cb = min(cb, MAX_CASHBACK)
    return _half_up(cb)


if __name__ == "__main__":
    print(cashback(10_000, "silver", False))   # 150  (1.50 บาท)
    print(cashback(10_000, "silver", True))    # 300
    print(cashback(10_100, "silver", False))   # 152  (151.5 ปัดขึ้น)
    print(cashback(1_000_000, "platinum", True))  # 20000 (ติด cap 200 บาท)
