"""ค่าปรับลูกค้าขายส่งที่ชำระช้า (BaanKafe)

กติกา:
- amount   = ยอดค้างชำระ หน่วยเป็นสตางค์ (จำนวนเต็ม >= 0)
- days_late = จำนวนวันที่ชำระช้า (จำนวนเต็ม 0-365)
- ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน คิดวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุด 15% ของยอดค้างชำระ
- คืนค่าปรับเป็นจำนวนเต็มสตางค์ ปัดครึ่งขึ้น ปัดครั้งเดียวตอนท้าย

ผิดชนิดหรือนอกช่วง -> ValueError
"""

import math
from fractions import Fraction

GRACE_DAYS = 3                     # ช้าไม่เกินนี้ไม่คิดค่าปรับ
MAX_DAYS = 365                     # ขอบบนของ days_late
DAILY_RATE = Fraction(75, 10000)   # 0.75% ต่อวัน
CAP_RATE = Fraction(15, 100)       # เพดาน 15% ของยอดค้างชำระ


# ---------- ตรวจข้อมูลนำเข้า (ผิดอะไรก็ ValueError) ----------

def _need_int(value, name, low=None, high=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


# ---------- ปัดเศษ ----------

def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 1.5 -> 2, 1.4 -> 1"""
    return math.floor(Fraction(x) + Fraction(1, 2))


# ---------- ฟังก์ชันหลัก ----------

def late_fee(amount, days_late):
    """คืนค่าปรับเป็นจำนวนเต็มสตางค์"""
    _need_int(amount, "amount", low=0)
    _need_int(days_late, "days_late", low=0, high=MAX_DAYS)

    if days_late <= GRACE_DAYS:
        return 0

    principal = Fraction(amount)
    fee = principal * DAILY_RATE * days_late   # นับทุกวันที่ช้า รวม 3 วันแรก
    cap = principal * CAP_RATE
    return _half_up(min(fee, cap))             # เพดาน แล้วปัดครั้งเดียว


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(late_fee(10000, 3))   # 0    (ไม่เกิน 3 วัน)
    print(late_fee(10000, 4))   # 300  (3% ของ 10000)
    print(late_fee(200, 4))     # 6
    print(late_fee(10000, 30))  # 1500 (ถึงเพดาน 15%)
