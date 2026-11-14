"""คิดเงินคืนสมาชิกของร้าน BaanKafe

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม) ไม่ใช้ float
"""

from fractions import Fraction

MIN_AMOUNT_SATANG = 10_000      # 100 บาท: ยอดต่ำกว่านี้ไม่ได้เงินคืน
MAX_CASHBACK_SATANG = 20_000    # 200 บาท: เงินคืนสูงสุดต่อบิล
BIRTHDAY_MULTIPLIER = 2         # เดือนเกิดได้เงินคืน 2 เท่า

RATES = {
    "silver": Fraction(15, 1000),   # 1.5%
    "gold": Fraction(25, 1000),     # 2.5%
    "platinum": Fraction(4, 100),   # 4%
}


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int, x ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def cashback(amount, tier, birthday):
    """คืนเงินคืนเป็นสตางค์ (int)

    amount   : ยอดซื้อเป็นสตางค์ (int, >= 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด
    """
    if type(amount) is not int:
        raise ValueError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if amount < 0:
        raise ValueError("amount ต้องไม่น้อยกว่า 0")
    if type(tier) is not str or tier not in RATES:
        raise ValueError(f"tier ต้องเป็นหนึ่งใน {sorted(RATES)}")
    if type(birthday) is not bool:
        raise ValueError("birthday ต้องเป็น True หรือ False")

    # ยอดต่ำกว่า 100 บาท ไม่ได้เงินคืน (ตรวจยอดซื้อจริง ก่อนคูณ 2 เท่า)
    if amount < MIN_AMOUNT_SATANG:
        return 0

    raw = Fraction(amount) * RATES[tier]          # ยังไม่ปัด
    if birthday:
        raw *= BIRTHDAY_MULTIPLIER                # คูณก่อนปัด

    rounded = _half_up(raw)                       # ปัดครั้งเดียว ตอนท้าย
    return min(rounded, MAX_CASHBACK_SATANG)      # cap หลังคำนวณทั้งหมด


if __name__ == "__main__":
    print(cashback(10_000, "silver", False))   # 150
    print(cashback(10_000, "gold", True))      # 500
    print(cashback(500_000, "platinum", False))  # 20000 (ถึงเพดาน)
