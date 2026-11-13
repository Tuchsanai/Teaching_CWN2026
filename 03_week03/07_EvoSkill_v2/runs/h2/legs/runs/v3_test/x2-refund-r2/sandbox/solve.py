import math
from fractions import Fraction

# กติกาการคืนเงินคอร์สสอนชงกาแฟ BaanKafe
# 1. คืนตามสัดส่วนของส่วนที่ยังไม่ได้เรียน: paid * (100 - used_percent) / 100
# 2. เรียนไปแล้วเกิน 80% (used_percent > 80) ไม่คืนเงิน
# 3. ถ้า restock เป็น True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน (คงเหลือ 87.5%)
# 4. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ครั้งเดียวที่ผลสุดท้าย

FEE_RATE = Fraction(125, 1000)  # 12.5%
MAX_USED_FOR_REFUND = 80


def _to_frac(x):
    """แปลงตัวเลขเป็น Fraction ผ่าน str เพื่อไม่ให้เกิดคลาดเคลื่อนจาก float"""
    return Fraction(str(x))


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ใช้ครั้งเดียวตอนคืนค่า)"""
    return math.floor(f + Fraction(1, 2))


def refund(paid, used_percent, restock):
    """คำนวณเงินที่ต้องคืนลูกค้า (สตางค์, จำนวนเต็ม)

    paid          เงินที่ลูกค้าจ่ายมา (สตางค์, ตั้งแต่ 0)
    used_percent  เรียนไปแล้วกี่เปอร์เซ็นต์ (จำนวนเต็ม 0-100)
    restock       True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    if isinstance(paid, bool) or isinstance(used_percent, bool):
        raise ValueError("paid และ used_percent ต้องเป็นตัวเลข")

    paid_f = _to_frac(paid)
    if paid_f < 0:
        raise ValueError("paid ต้องไม่ติดลบ")

    used_f = _to_frac(used_percent)
    if used_f != int(used_f) or not (0 <= used_f <= 100):
        raise ValueError("used_percent ต้องเป็นจำนวนเต็มในช่วง 0-100")
    used = int(used_f)

    if used > MAX_USED_FOR_REFUND:
        return 0

    amount = paid_f * Fraction(100 - used, 100)

    if restock:
        amount = amount * (1 - FEE_RATE)

    return _round_half_up(amount)
