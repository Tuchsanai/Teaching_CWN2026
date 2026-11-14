"""BaanKafe: หารบิล (split_bill)

กฎ:
1. ยอดที่ต้องหาร = ยอดบิล + ทิป, ทิป = ยอดบิล * tip_percent / 100
2. ทิปเป็นเงินที่ลูกค้าจ่ายเข้าร้าน จึงปัดครึ่งขึ้น (half up) ครั้งเดียวเป็นสตางค์
3. หารให้เท่ากันทุกคน ถ้าไม่ลงตัว คนลำดับต้น ๆ จ่ายเพิ่มคนละ 1 สตางค์จนครบ

ไม่มี side effect ตอน import
"""

import math
from fractions import Fraction


# ---------- ตรวจข้อมูลนำเข้า (รับเฉพาะ int จริง, ผิดอะไรก็ ValueError) ----------

def _need_int(value, name, low=None, high=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


# ---------- ปัดเศษ (ใช้ครั้งเดียวตอนท้ายของแต่ละขั้น) ----------

def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


# ---------- การหาร ----------

def _split_even(total, people):
    """หาร total (จำนวนเต็ม) ให้ people คน เศษให้คนลำดับต้น ๆ คนละ 1 หน่วย"""
    base, rem = divmod(total, people)
    return [base + 1] * rem + [base] * (people - rem)


def split_bill(total, people, tip_percent):
    """คืน list ของยอดที่แต่ละคนจ่าย (สตางค์ จำนวนเต็ม) เรียงตามลำดับคน

    total: ยอดบิลเป็นสตางค์ (>= 0)
    people: จำนวนคน (>= 1)
    tip_percent: ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0-100)
    """
    total = _need_int(total, "total", low=0)
    people = _need_int(people, "people", low=1)
    tip_percent = _need_int(tip_percent, "tip_percent", low=0, high=100)

    tip = _half_up(Fraction(total * tip_percent, 100))
    grand_total = total + tip
    return _split_even(grand_total, people)


if __name__ == "__main__":
    print(split_bill(10000, 3, 10))
    print(split_bill(0, 4, 0))
