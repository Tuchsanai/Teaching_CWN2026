import math
from fractions import Fraction

# กติกาการคืนเงินคอร์สสอนชงกาแฟ BaanKafe
# 1. เรียนไปแล้วเกิน 80% -> ไม่คืนเงิน (0 สตางค์)
# 2. คืนตามสัดส่วนที่ยังไม่ได้เรียน = paid * (100 - used_percent) / 100
# 3. ถ้า restock = True -> หักค่าดำเนินการ 12.5% ของยอดที่จะคืน (คงเหลือ 87.5%)
# 4. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ ครั้งเดียวที่ค่าที่คืน


def _to_frac(x):
    """แปลงตัวเลขเป็น Fraction โดยไม่เกิดคลาดเคลื่อนจาก float"""
    return Fraction(str(x))


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ใช้กับค่าที่ไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def refund(paid, used_percent, restock):
    """คำนวณเงินที่ต้องคืนลูกค้า (สตางค์, จำนวนเต็ม)

    paid          เงินที่ลูกค้าจ่ายมา (สตางค์ ตั้งแต่ 0)
    used_percent  เรียนไปแล้วกี่เปอร์เซ็นต์ (จำนวนเต็ม 0-100)
    restock       True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    """
    # ตรวจอินพุต (bool ไม่นับเป็นตัวเลข)
    if isinstance(paid, bool) or isinstance(used_percent, bool):
        raise ValueError("paid และ used_percent ต้องเป็นตัวเลข")

    paid_f = _to_frac(paid)
    if paid_f < 0:
        raise ValueError("paid ต้องไม่ติดลบ")

    used_f = _to_frac(used_percent)
    if used_f.denominator != 1 or not (0 <= used_f <= 100):
        raise ValueError("used_percent ต้องเป็นจำนวนเต็มระหว่าง 0-100")
    used = int(used_f)

    # เรียนไปแล้วเกิน 80% ไม่คืนเงิน
    if used > 80:
        return 0

    # คืนตามสัดส่วนที่ยังไม่ได้เรียน (ยังไม่ปัด)
    amount = paid_f * Fraction(100 - used, 100)

    # หักค่าดำเนินการ 12.5% = เหลือ 87.5% ของยอดที่จะคืน
    if restock:
        amount = amount * Fraction(7, 8)

    return _round_half_up(amount)
