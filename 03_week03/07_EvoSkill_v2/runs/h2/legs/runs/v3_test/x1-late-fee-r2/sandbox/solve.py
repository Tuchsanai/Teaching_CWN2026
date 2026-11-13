import math
from fractions import Fraction

GRACE_DAYS = 3                    # ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
DAILY_RATE = Fraction(75, 10000)  # 0.75% ของยอดค้างชำระต่อวัน
MAX_RATE = Fraction(15, 100)      # เพดาน 15% ของยอดค้างชำระ
MAX_DAYS = 365


def _to_fraction(x, name):
    """แปลงตัวเลขเป็น Fraction ผ่านข้อความ เพื่อไม่ให้เกิดคลาดเคลื่อนจาก float"""
    if isinstance(x, bool):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    try:
        return Fraction(str(x))
    except (ValueError, TypeError, ZeroDivisionError):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")


def late_fee(amount, days_late):
    """คืนค่าปรับ (สตางค์ จำนวนเต็ม) ของยอดค้างชำระ amount (สตางค์) ที่ชำระช้า days_late วัน

    - ช้าไม่เกิน 3 วัน: ไม่มีค่าปรับ
    - ช้าเกิน 3 วัน: 0.75% ต่อวันของยอดค้าง นับทุกวันที่ช้า (รวม 3 วันแรก)
    - ค่าปรับสูงสุด 15% ของยอดค้าง
    - ปัดครึ่งขึ้นครั้งเดียวที่ผลสุดท้าย
    """
    amt = _to_fraction(amount, "amount")
    if amt < 0:
        raise ValueError("amount ต้องไม่ติดลบ")

    days = _to_fraction(days_late, "days_late")
    if days.denominator != 1 or not (0 <= days <= MAX_DAYS):
        raise ValueError("days_late ต้องเป็นจำนวนเต็ม 0–365")
    days = int(days)

    if days <= GRACE_DAYS:
        return 0

    fee = amt * days * DAILY_RATE
    fee = min(fee, amt * MAX_RATE)
    return math.floor(fee + Fraction(1, 2))  # ปัดครึ่งขึ้น
