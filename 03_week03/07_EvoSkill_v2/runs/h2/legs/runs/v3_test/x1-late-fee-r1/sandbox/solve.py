"""BaanKafe: คำนวณค่าปรับลูกค้าขายส่งที่ชำระเงินช้า

กติกา (ตามลำดับ):
1. ช้าไม่เกิน 3 วัน (days_late <= 3) ไม่คิดค่าปรับ
2. ช้าเกิน 3 วัน คิดค่าปรับวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
3. ค่าปรับสูงสุดไม่เกิน 15% ของยอดค้างชำระ
4. คืนค่าปรับเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้นครั้งเดียวที่ผลสุดท้าย)
"""

import math
from fractions import Fraction

MAX_DAYS_LATE = 365
GRACE_DAYS = 3
DAILY_RATE = Fraction(75, 10000)   # 0.75% ต่อวัน
MAX_RATE = Fraction(15, 100)       # 15% เพดาน


def _to_frac(x):
    """แปลงตัวเลขเป็น Fraction ผ่าน str เพื่อไม่ให้เกิดคลาดเคลื่อนจาก float"""
    return Fraction(str(x))


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ยอดไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def late_fee(amount, days_late):
    """คืนค่าปรับ (สตางค์, int) สำหรับยอดค้างชำระ amount (สตางค์) ที่ชำระช้า days_late วัน"""
    if isinstance(amount, bool) or isinstance(days_late, bool):
        raise ValueError("amount และ days_late ต้องเป็นตัวเลข")
    if not isinstance(days_late, int):
        if isinstance(days_late, float) and days_late.is_integer():
            days_late = int(days_late)
        else:
            raise ValueError("days_late ต้องเป็นจำนวนเต็ม")
    if not 0 <= days_late <= MAX_DAYS_LATE:
        raise ValueError(f"days_late ต้องอยู่ระหว่าง 0 ถึง {MAX_DAYS_LATE}")

    principal = _to_frac(amount)
    if principal.denominator != 1:
        raise ValueError("amount ต้องเป็นจำนวนเต็มสตางค์")
    if principal < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    if days_late <= GRACE_DAYS:
        return 0

    fee = principal * DAILY_RATE * days_late
    cap = principal * MAX_RATE
    fee = min(fee, cap)
    return int(_round_half_up(fee))
