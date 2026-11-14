"""คิดเงินคืนของคอร์สสอนชงกาแฟ BaanKafe

กติกา (ตามโจทย์):
1. paid = เงินที่ลูกค้าจ่าย (สตางค์, จำนวนเต็ม >= 0)
2. used_percent = เรียนไปแล้วกี่เปอร์เซ็นต์ (จำนวนเต็ม 0-100)
3. restock = True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน, False ไม่หัก
4. คืนเงินตามสัดส่วนที่ยังไม่ได้เรียน: paid * (100 - used_percent) / 100
5. เรียนไปแล้วเกิน 80% (used_percent > 80) ไม่คืนเงิน -> 0
6. ผลลัพธ์เป็นจำนวนเต็มสตางค์

การตีความที่โจทย์ไม่ได้ระบุ:
- ที่ 80% พอดี ถือว่ายังคืนเงินได้ (กฎคือ "เกิน 80%")
- วิธีปัดเศษ: ปัดลง (เงินที่ร้านจ่ายออกให้ลูกค้า) เพื่อไม่ให้ร้านจ่ายเกิน
- ตรวจ input ก่อนเงื่อนไข 80% เพื่อให้ค่าผิดไม่คืน 0 เงียบ ๆ
- คำนวณทั้งหมดด้วย Fraction ปัดครั้งเดียวตอนท้าย
"""

import math
from fractions import Fraction


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


# ---------- ตัวช่วยปัด ----------

def _round_down(x):
    """ปัดลงเป็นจำนวนเต็ม (x ไม่ติดลบ): 87.5 -> 87"""
    return math.floor(Fraction(x))


# ---------- ฟังก์ชันหลัก ----------

REFUND_CUTOFF_PERCENT = 80      # เรียนเกินนี้ไม่คืนเงิน
RESTOCK_FEE = Fraction(125, 1000)  # 12.5%


def refund(paid, used_percent, restock):
    """คืนค่าเงินที่ต้องคืนลูกค้า (สตางค์, จำนวนเต็ม)

    paid: เงินที่จ่ายมา (สตางค์, int >= 0)
    used_percent: เปอร์เซ็นต์ที่เรียนไปแล้ว (int 0-100)
    restock: True หักค่าดำเนินการ 12.5%, False ไม่หัก
    """
    # 1) ตรวจ input ทุกตัวก่อนเงื่อนไขธุรกิจ
    paid = _need_int(paid, "paid", low=0)
    used_percent = _need_int(used_percent, "used_percent", low=0, high=100)
    restock = _need_bool(restock, "restock")

    # 2) เกินเกณฑ์ ไม่คืนเงิน
    if used_percent > REFUND_CUTOFF_PERCENT:
        return 0

    # 3) คืนตามสัดส่วนที่ยังไม่ได้เรียน (exact)
    amount = Fraction(paid) * (100 - used_percent) / 100

    # 4) หักค่าดำเนินการ (ยังไม่ปัด)
    if restock:
        amount = amount * (1 - RESTOCK_FEE)

    # 5) ปัดครั้งเดียวตอนท้าย
    return _round_down(amount)


if __name__ == "__main__":
    print("refund(10000, 30, False) =", refund(10000, 30, False))
    print("refund(10000, 30, True)  =", refund(10000, 30, True))
    print("refund(10000, 80, True)  =", refund(10000, 80, True))
    print("refund(10000, 81, False) =", refund(10000, 81, False))
