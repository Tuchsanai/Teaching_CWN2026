"""BaanKafe: ฟังก์ชันหารบิล split_bill(total, people, tip_percent)

กติกา
- total        = ยอดบิล (สตางค์, จำนวนเต็ม >= 0)
- people       = จำนวนคน (จำนวนเต็ม >= 1)
- tip_percent  = ทิปเป็นเปอร์เซ็นต์ (จำนวนเต็ม 0-100)
- ยอดที่ต้องหาร = ยอดบิล + ทิป  (ทิปคิดจากยอดบิล แล้วปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียวตอนท้าย)
- หารเท่ากัน ถ้าไม่ลงตัว คนลำดับต้น ๆ จ่ายเพิ่มคนละ 1 สตางค์
- คืน list ของยอดที่แต่ละคนจ่าย (จำนวนเต็มสตางค์) เรียงตามลำดับคน

ผิดชนิดหรือนอกช่วง -> ValueError เท่านั้น
ไม่มี side effect ตอน import
"""

import math
from fractions import Fraction


# ---------- ตรวจข้อมูลนำเข้า (ชนิดเข้มงวด: ไม่รับ bool/float/str) ----------

def _need_int(value, name, low=None, high=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


# ---------- ปัดเศษและหาร ----------

def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


def _split_even(total, people):
    """หาร total ให้ people คน เศษให้คนลำดับต้น ๆ คนละ 1 สตางค์"""
    base, rem = divmod(total, people)
    return [base + 1] * rem + [base] * (people - rem)


# ---------- ฟังก์ชันหลัก ----------

def split_bill(total, people, tip_percent):
    """คืน list ของยอดที่แต่ละคนจ่าย (สตางค์, จำนวนเต็ม) เรียงตามลำดับคน"""
    total = _need_int(total, "total", low=0)
    people = _need_int(people, "people", low=1)
    tip_percent = _need_int(tip_percent, "tip_percent", low=0, high=100)

    # ยอดบิล + ทิป = total * (100 + tip%) / 100 ; ปัดครั้งเดียวตอนท้ายแล้วค่อยหาร
    amount_due = _half_up(Fraction(total) * (100 + tip_percent) / 100)
    return _split_even(amount_due, people)


if __name__ == "__main__":
    assert split_bill(10000, 3, 10) == [3667, 3667, 3666]
    assert split_bill(333, 1, 50) == [500]
    print("solve ok:", split_bill(10000, 3, 10))
