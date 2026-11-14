"""BaanKafe: หารบิลให้ลูกค้าหลายคน (หน่วยสตางค์ จำนวนเต็มล้วน)

split_bill(total, people, tip_percent) -> list[int]
- total        ยอดบิลเป็นสตางค์ (>= 0)
- people       จำนวนคน (>= 1)
- tip_percent  ทิปเป็นเปอร์เซ็นต์ จำนวนเต็ม 0-100

ยอดที่ต้องหาร = total + ทิป (ทิปคิดจาก total แล้วปัดครึ่งขึ้นครั้งเดียวตอนท้าย)
หารเท่ากันทุกคน เศษสตางค์ให้คนลำดับต้น ๆ คนละ 1 สตางค์
"""

import math
from fractions import Fraction


# ---------- ตรวจข้อมูลนำเข้า (ผิดชนิดหรือนอกช่วง -> ValueError เท่านั้น) ----------

def need_int(value, name, low=None, high=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


# ---------- ปัดเศษ ----------

def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


# ---------- การหาร ----------

def split_even(total, people):
    """หาร total (จำนวนเต็ม) ให้ people คน เศษให้คนลำดับต้น ๆ คนละ 1 หน่วย"""
    base, rem = divmod(total, people)
    return [base + 1] * rem + [base] * (people - rem)


# ---------- ฟังก์ชันหลัก ----------

def split_bill(total, people, tip_percent):
    """คืน list ยอดที่แต่ละคนจ่าย (สตางค์ จำนวนเต็ม) เรียงตามลำดับคน"""
    need_int(total, "total", low=0)
    need_int(people, "people", low=1)
    need_int(tip_percent, "tip_percent", low=0, high=100)

    # ทิปคำนวณจากยอดบิลแล้วปัดครั้งเดียวตอนท้าย (exact ด้วย Fraction)
    amount = half_up(Fraction(total) * (100 + tip_percent) / 100)
    return split_even(amount, people)


if __name__ == "__main__":
    print(split_bill(10000, 3, 0))    # [3334, 3333, 3333]
    print(split_bill(10000, 3, 10))   # [3667, 3667, 3666]
