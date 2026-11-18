"""ค่าปรับการชำระเงินช้าของลูกค้าขายส่ง BaanKafe

กฎ:
1. ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
2. ช้าเกิน 3 วัน คิด 0.75% ของยอดค้างชำระต่อวัน นับทุกวันที่ช้า (รวม 3 วันแรก)
3. ค่าปรับสูงสุด 15% ของยอดค้างชำระ
4. คืนค่าปรับเป็นจำนวนเต็มสตางค์

การตีความที่โจทย์ไม่ได้ระบุ:
- ปัดเศษแบบครึ่งขึ้น (ค่าปรับเป็นเงินที่ลูกค้าจ่ายเข้าร้าน ตามแนวทาง skill money-arithmetic-rounding)
- ใช้เพดานก่อนปัดครั้งเดียวตอนท้าย (ผลเท่ากับปัดหลังเพดานเมื่อเพดานเป็นจำนวนเต็ม)
"""

import math
from fractions import Fraction

GRACE_DAYS = 3                      # ช้าไม่เกินนี้ไม่คิดค่าปรับ
DAILY_RATE = Fraction(75, 10000)    # 0.75% ต่อวัน
CAP_RATE = Fraction(15, 100)        # เพดาน 15% ของยอดค้างชำระ
MAX_DAYS = 365


# ---------- ตรวจข้อมูลนำเข้า (คัดลอกจาก skill strict-input-validation) ----------

def need_int(value, name, low=None, high=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


# ---------- ปัดเศษ (คัดลอกจาก skill money-arithmetic-rounding) ----------

def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


# ---------- ฟังก์ชันหลัก ----------

def late_fee(amount, days_late):
    """คืนค่าปรับการชำระเงินช้าเป็นสตางค์ (จำนวนเต็ม)

    amount: ยอดค้างชำระ หน่วยสตางค์ (จำนวนเต็ม >= 0)
    days_late: จำนวนวันที่ช้า (จำนวนเต็ม 0-365)
    """
    # ตรวจ input ก่อนเงื่อนไขธุรกิจทุกชนิด
    need_int(amount, "amount", low=0)
    need_int(days_late, "days_late", low=0, high=MAX_DAYS)

    if days_late <= GRACE_DAYS:
        return 0

    fee = Fraction(amount) * DAILY_RATE * days_late   # ยังไม่ปัด
    cap = Fraction(amount) * CAP_RATE                 # ยังไม่ปัด
    return half_up(min(fee, cap))                     # ปัดครั้งเดียวตอนท้าย


if __name__ == "__main__":
    print("ช้า 3 วัน, ยอด 10000 สต. ->", late_fee(10000, 3))   # 0
    print("ช้า 4 วัน, ยอด 10000 สต. ->", late_fee(10000, 4))   # 300
    print("ช้า 365 วัน, ยอด 10000 สต. ->", late_fee(10000, 365))  # 1500 (เพดาน)
