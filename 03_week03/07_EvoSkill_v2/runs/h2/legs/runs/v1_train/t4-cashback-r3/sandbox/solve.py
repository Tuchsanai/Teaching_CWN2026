"""BaanKafe cashback calculator.

หน่วยทั้งหมดเป็นสตางค์ (1 บาท = 100 สตางค์) คำนวณด้วย Fraction แล้วปัดครั้งเดียวที่ขั้นสุดท้าย

ลำดับการคิด:
1. ยอดต่ำกว่า 100 บาท (10000 สตางค์) -> ไม่ได้เงินคืน (0)
2. เงินคืนดิบ = ยอด × อัตราตามระดับสมาชิก (silver 1.5%, gold 2.5%, platinum 4%)
3. ถ้าซื้อในเดือนเกิด -> คูณ 2
4. ปัดเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น)
5. ตัดเพดานสูงสุด 200 บาท (20000 สตางค์) ต่อบิล
"""

from fractions import Fraction
import math

MIN_AMOUNT_SATANG = 100 * 100      # 100 บาท
MAX_CASHBACK_SATANG = 200 * 100    # 200 บาทต่อบิล
BIRTHDAY_MULTIPLIER = 2

RATE_PERCENT = {
    "silver": Fraction(15, 10),    # 1.5%
    "gold": Fraction(25, 10),      # 2.5%
    "platinum": Fraction(4),       # 4%
}


def _round_half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ)"""
    return math.floor(x + Fraction(1, 2))


def cashback(amount, tier, birthday=False):
    """คืนค่าเงินคืนเป็นจำนวนเต็มสตางค์

    amount   : ยอดซื้อ หน่วยสตางค์ (int, >= 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    key = str(tier).strip().lower() if tier is not None else ""
    if key not in RATE_PERCENT:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r} (ต้องเป็น silver, gold หรือ platinum)")

    # 1. เกณฑ์ขั้นต่ำ ตรวจจากยอดตั้งต้น
    if amount < MIN_AMOUNT_SATANG:
        return 0

    # 2-3. อัตรา และคูณ 2 ถ้าเดือนเกิด (เก็บเป็น Fraction ยังไม่ปัด)
    raw = Fraction(amount) * RATE_PERCENT[key] / 100
    if birthday:
        raw *= BIRTHDAY_MULTIPLIER

    # 4-5. ปัดครั้งเดียว แล้วตัดเพดาน
    return min(_round_half_up(raw), MAX_CASHBACK_SATANG)
