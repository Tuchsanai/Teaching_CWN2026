"""BaanKafe cashback calculator.

หน่วยทั้งหมดเป็นสตางค์ (1 บาท = 100 สตางค์)
"""

import math
from fractions import Fraction

# อัตราเงินคืนตามระดับสมาชิก
RATES = {
    "silver": Fraction(15, 1000),   # 1.5%
    "gold": Fraction(25, 1000),     # 2.5%
    "platinum": Fraction(40, 1000), # 4%
}

MIN_AMOUNT = 100 * 100      # ยอดซื้อขั้นต่ำ 100 บาท = 10000 สตางค์ (ต่ำกว่านี้ไม่ได้เงินคืน)
BIRTHDAY_MULTIPLIER = 2     # เดือนเกิดได้เงินคืน 2 เท่า
MAX_CASHBACK = 200 * 100    # เงินคืนสูงสุดต่อบิล 200 บาท = 20000 สตางค์


def _round_half_up(value):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม ใช้ครั้งเดียวตอนคืนค่า (ค่าไม่ติดลบ)"""
    return math.floor(value + Fraction(1, 2))


def cashback(amount, tier, birthday):
    """คำนวณเงินคืนสมาชิกของบิลหนึ่งใบ (คืนค่าเป็นจำนวนเต็มสตางค์)

    amount   : ยอดซื้อ (สตางค์ ตั้งแต่ 0)
    tier     : "silver", "gold" หรือ "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด
    """
    # ตรวจอินพุต
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise ValueError("amount ต้องเป็นตัวเลข (สตางค์)")
    if amount != int(amount):
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์")
    amount = int(amount)
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    if not isinstance(tier, str) or tier.strip().lower() not in RATES:
        raise ValueError(f"tier ไม่รู้จัก: {tier!r} (ใช้ silver, gold หรือ platinum)")
    rate = RATES[tier.strip().lower()]

    # ยอดต่ำกว่า 100 บาท ไม่ได้เงินคืน
    if amount < MIN_AMOUNT:
        return 0

    # อัตรา x ตัวคูณเดือนเกิด (ถ้ามี) แล้วจึงเทียบเพดานต่อบิล
    cashback_exact = Fraction(amount) * rate
    if birthday:
        cashback_exact *= BIRTHDAY_MULTIPLIER

    capped = min(cashback_exact, Fraction(MAX_CASHBACK))
    return int(_round_half_up(capped))
