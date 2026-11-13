"""BaanKafe cashback calculator.

หน่วย: amount และผลลัพธ์เป็นสตางค์ (1 บาท = 100 สตางค์)

กติกา (ตามลำดับ):
1. ยอดซื้อต่ำกว่า 100 บาท (10000 สตางค์) ไม่ได้เงินคืน -> 0
2. อัตราตามระดับสมาชิก: silver 1.5%, gold 2.5%, platinum 4%
3. ซื้อในเดือนเกิด (birthday=True) ได้เงินคืน 2 เท่า
4. เงินคืนสูงสุด 200 บาท (20000 สตางค์) ต่อบิล (cap หลังคูณเดือนเกิดแล้ว)
5. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ ปัดครั้งเดียวตอนคืนค่า
"""

import math
from fractions import Fraction

MIN_PURCHASE = 100 * 100        # 100 บาท เป็นสตางค์
CAP = 200 * 100                 # 200 บาท เป็นสตางค์
BIRTHDAY_MULTIPLIER = 2

RATES = {
    "silver": Fraction(15, 1000),    # 1.5%
    "gold": Fraction(25, 1000),      # 2.5%
    "platinum": Fraction(40, 1000),  # 4%
}


def _to_satang(amount):
    """รับเฉพาะตัวเลขที่เป็นจำนวนเต็มสตางค์ (int หรือ float ที่ค่าเป็นจำนวนเต็ม)"""
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise ValueError("amount ต้องเป็นตัวเลข")
    if isinstance(amount, float):
        if not amount.is_integer():
            raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์")
        amount = int(amount)
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    return amount


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ยอดไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def cashback(amount, tier, birthday):
    """คืนค่าเงินคืนเป็นจำนวนเต็มสตางค์

    amount   : ยอดซื้อ (สตางค์ ตั้งแต่ 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True คือซื้อในเดือนเกิด
    """
    amount = _to_satang(amount)

    if tier not in RATES:
        raise ValueError(f"tier ไม่รู้จัก: {tier!r}")

    if amount < MIN_PURCHASE:
        return 0

    back = Fraction(amount) * RATES[tier]
    if birthday:
        back *= BIRTHDAY_MULTIPLIER

    return min(_round_half_up(back), CAP)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(cashback(10000, "silver", False))   # 150 สตางค์ (1.50 บาท)
    print(cashback(50000, "gold", True))      # 2500 สตางค์ (25 บาท)
    print(cashback(1000000, "platinum", True))  # 20000 สตางค์ (cap 200 บาท)
