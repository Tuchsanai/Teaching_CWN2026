"""คิดเงินคืนคอร์สสอนชงกาแฟ ของร้าน BaanKafe

กติกา:
1. paid         = เงินที่ลูกค้าจ่าย (สตางค์ ตั้งแต่ 0)
2. used_percent = เรียนไปแล้วกี่เปอร์เซ็นต์ (จำนวนเต็ม 0–100)
3. restock      = True คือหักค่าดำเนินการ 12.5% ของยอดที่จะคืน
4. คืนตามสัดส่วนที่ยังไม่ได้เรียน: paid * (100 - used_percent) / 100
5. เรียนไปแล้วเกิน 80% ไม่คืนเงิน (คืน 0)
6. คำนวณแบบ Fraction ปัดลงครั้งเดียวตอนท้าย -> จำนวนเต็มสตางค์
   (เป็นเงินที่ร้านจ่ายออกให้ลูกค้า จึงปัดลงเพื่อไม่ให้จ่ายเกิน)

ผิดชนิดหรือนอกช่วง -> ValueError เท่านั้น
"""

import math
from fractions import Fraction

USED_LIMIT_PERCENT = 80          # เรียนเกินค่านี้ไม่คืนเงิน
FEE_RATE = Fraction(125, 1000)   # ค่าดำเนินการ 12.5%


# ---------- ตรวจข้อมูลนำเข้า (คัดลอกจาก money_helpers / validators) ----------

def _need_int(value, name, low=None, high=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


def _need_bool(value, name):
    """flag: ต้องเป็น True หรือ False จริง"""
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


# ---------- ปัดเศษ ----------

def _round_down(x):
    """ปัดลงเป็นจำนวนเต็ม (x ไม่ติดลบ): 50.5 -> 50"""
    return math.floor(Fraction(x))


# ---------- ฟังก์ชันหลัก ----------

def refund(paid, used_percent, restock):
    """คืนค่าเงินที่ต้องคืนลูกค้า (สตางค์ จำนวนเต็ม)"""
    # ตรวจ input ทุกตัวก่อน แล้วค่อยเข้าเงื่อนไขธุรกิจ
    _need_int(paid, "paid", low=0)
    _need_int(used_percent, "used_percent", low=0, high=100)
    _need_bool(restock, "restock")

    if used_percent > USED_LIMIT_PERCENT:
        return 0

    amount = Fraction(paid) * (100 - used_percent) / 100
    if restock:
        amount -= amount * FEE_RATE
    return _round_down(amount)


if __name__ == "__main__":
    print(refund(10000, 0, False))   # 10000
    print(refund(10000, 50, False))  # 5000
    print(refund(10000, 50, True))   # 4375
    print(refund(10000, 81, True))   # 0
