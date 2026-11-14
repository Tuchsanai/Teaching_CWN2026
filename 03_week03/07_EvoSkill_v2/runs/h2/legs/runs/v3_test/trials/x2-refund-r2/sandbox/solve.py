"""คิดเงินคืนคอร์สสอนชงกาแฟ BaanKafe

refund(paid, used_percent, restock)
- paid: เงินที่ลูกค้าจ่ายมา (สตางค์, จำนวนเต็ม >= 0)
- used_percent: เรียนไปแล้วกี่เปอร์เซ็นต์ (จำนวนเต็ม 0-100)
- restock: True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
คืนค่า: เงินที่ต้องคืนลูกค้า (สตางค์, จำนวนเต็ม)

ไม่มี side effect ตอน import
"""

import math
from fractions import Fraction

USED_LIMIT = 80                      # เรียนเกิน 80% ไม่คืนเงิน (80 พอดียังคืนได้)
RESTOCK_FEE = Fraction(125, 1000)    # ค่าดำเนินการ 12.5%


# ---------- ตรวจข้อมูลนำเข้า (ผิดชนิดหรือนอกช่วง -> ValueError เท่านั้น) ----------

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
    """ปัดลงเป็นจำนวนเต็ม (x ไม่ติดลบ): เงินที่ร้านจ่ายออกให้ลูกค้า ไม่ให้จ่ายเกิน"""
    return math.floor(Fraction(x))


# ---------- ฟังก์ชันหลัก ----------

def refund(paid, used_percent, restock):
    """คำนวณเงินคืนของคอร์ส (หน่วยสตางค์ ปัดลงครั้งเดียวตอนท้าย)"""
    # 1) ตรวจ input ทั้งหมดก่อนเงื่อนไขธุรกิจ
    _need_int(paid, "paid", low=0)
    _need_int(used_percent, "used_percent", low=0, high=100)
    _need_bool(restock, "restock")

    # 2) เงื่อนไขธุรกิจ: เรียนเกิน 80% ไม่คืนเงิน
    if used_percent > USED_LIMIT:
        return 0

    # 3) คืนตามสัดส่วนที่ยังไม่ได้เรียน (exact ด้วย Fraction ยังไม่ปัด)
    amount = Fraction(paid) * (100 - used_percent) / 100

    # 4) หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
    if restock:
        amount -= amount * RESTOCK_FEE

    # 5) ปัดครั้งเดียวตอนท้าย
    return _round_down(amount)


if __name__ == "__main__":
    print(refund(10000, 20, False))  # 8000
    print(refund(10000, 20, True))   # 7000
    print(refund(10000, 81, False))  # 0
