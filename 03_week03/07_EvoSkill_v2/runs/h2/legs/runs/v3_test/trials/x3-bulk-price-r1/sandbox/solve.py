"""BaanKafe: คิดราคาขายส่งเมล็ดกาแฟ

หน่วยเงินทั้งหมดเป็นสตางค์ (จำนวนเต็ม). อัตราส่วนลดและ VAT ใช้ Fraction ไม่ใช้ float.
ลำดับการคิด:
  1. ยอดดิบ = unit_price * qty
  2. ส่วนลดตามจำนวนถุง (ใช้อัตราเดียว): >= 50 ถุง ลด 7.5%, >= 10 ถุง ลด 3.5%, น้อยกว่านั้นไม่ลด
  3. ถ้ามีคูปอง ลดอีก 2.5% จากยอดที่เหลือ (คูณต่อจากข้อ 2)
  4. บวก VAT 7% เป็นขั้นสุดท้าย
  5. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ ครั้งเดียวตอนท้าย (ยอดที่ลูกค้าจ่ายเข้าร้าน)
"""

import math
from fractions import Fraction


# ---------- ตรวจข้อมูลนำเข้า (ผิดชนิดหรือนอกช่วง -> ValueError) ----------

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

def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


# ---------- ฟังก์ชันหลัก ----------

BULK_TIER_50 = 50          # ซื้อตั้งแต่ 50 ถุงขึ้นไป
BULK_TIER_10 = 10          # ซื้อตั้งแต่ 10 ถุงขึ้นไป
RATE_50 = Fraction(75, 1000)   # 7.5%
RATE_10 = Fraction(35, 1000)   # 3.5%
COUPON_RATE = Fraction(25, 1000)  # 2.5%
VAT_RATE = Fraction(7, 100)       # 7%


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    unit_price: ราคาต่อถุง (สตางค์, จำนวนเต็ม >= 0)
    qty:        จำนวนถุง (จำนวนเต็ม 1–1000)
    coupon:     True ถ้ามีคูปอง
    """
    _need_int(unit_price, "unit_price", low=0)
    _need_int(qty, "qty", low=1, high=1000)
    _need_bool(coupon, "coupon")

    # 1. ยอดดิบ (exact)
    total = Fraction(unit_price * qty)

    # 2. ส่วนลดขั้นบันไดตามจำนวนถุง (อัตราเดียว ไม่สะสม)
    if qty >= BULK_TIER_50:
        rate = RATE_50
    elif qty >= BULK_TIER_10:
        rate = RATE_10
    else:
        rate = Fraction(0)
    total *= 1 - rate

    # 3. คูปองลดอีก 2.5% จากยอดที่เหลือ
    if coupon:
        total *= 1 - COUPON_RATE

    # 4. VAT 7% เป็นขั้นสุดท้าย
    total *= 1 + VAT_RATE

    # 5. ปัดครั้งเดียวตอนท้าย
    return _half_up(total)


if __name__ == "__main__":
    # ตัวอย่างและ self-check (ค่า expected คำนวณด้วย Fraction)
    assert bulk_price(10000, 1, False) == 10700          # 100 บาท 1 ถุง + VAT
    assert bulk_price(10000, 9, False) == 96300          # ไม่ถึง 10 ถุง ไม่ลด: 90000 * 1.07
    assert bulk_price(10000, 10, False) == 103255        # 100000 * 0.965 * 1.07 (ลด 3.5%)
    assert bulk_price(10000, 49, False) == 505950        # 490000 * 0.965 * 1.07 = 505949.5 -> ปัดครึ่งขึ้น
    assert bulk_price(10000, 50, True) == 482503         # 500000 * 0.925 * 0.975 * 1.07 = 482503.125
    assert bulk_price(0, 1000, True) == 0
    print("solve ok")
