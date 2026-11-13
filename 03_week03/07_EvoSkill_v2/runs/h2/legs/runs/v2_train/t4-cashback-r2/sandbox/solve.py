"""คิดเงินคืนสมาชิกของร้านกาแฟ BaanKafe

หน่วยทั้งหมดเป็นสตางค์ ผลลัพธ์เป็นจำนวนเต็มสตางค์
"""

import math
from fractions import Fraction

# อัตราเงินคืนของแต่ละระดับสมาชิก (ไม่ใช้ float)
RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(40, 1000),  # 4%
}

MIN_AMOUNT = 100 * 100        # ยอดซื้อขั้นต่ำ 100 บาท (สตางค์)
MAX_CASHBACK = 200 * 100      # เงินคืนสูงสุดต่อบิล 200 บาท (สตางค์)
BIRTHDAY_MULTIPLIER = 2       # เดือนเกิดได้เงินคืน 2 เท่า


def _to_fraction(value):
    """แปลงตัวเลขเป็น Fraction โดยไม่เกิดคลาดเคลื่อนจาก float"""
    if isinstance(value, bool) or not isinstance(value, (int, float, Fraction)):
        raise ValueError(f"amount ต้องเป็นตัวเลข ได้ {value!r}")
    return Fraction(str(value)) if isinstance(value, float) else Fraction(value)


def _round_half_up(value):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ใช้ครั้งเดียวตอนคืนค่า, ค่าไม่ติดลบ)"""
    return math.floor(value + Fraction(1, 2))


def cashback(amount, tier, birthday):
    """คืนจำนวนเงินคืนสมาชิก (สตางค์, int)

    amount   : ยอดซื้อ หน่วยสตางค์ ตั้งแต่ 0
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด
    """
    total = _to_fraction(amount)
    if total < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    key = tier.lower() if isinstance(tier, str) else tier
    if key not in RATES:
        raise ValueError(f"tier ไม่รู้จัก: {tier!r}")

    # ยอดต่ำกว่า 100 บาท ไม่ได้เงินคืน
    if total < MIN_AMOUNT:
        return 0

    result = total * RATES[key]
    if birthday:
        result *= BIRTHDAY_MULTIPLIER

    # เพดานใช้กับผลสุดท้ายหลังคูณทุกตัว
    result = min(result, Fraction(MAX_CASHBACK))
    return _round_half_up(result)


if __name__ == "__main__":
    print(cashback(100000, "silver", False))    # 1000 บาท silver -> 1500
    print(cashback(100000, "silver", True))     # เดือนเกิด -> 3000
    print(cashback(1000000, "platinum", False)) # 4% = 40000 -> เพดาน 20000
