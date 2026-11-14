"""BaanKafe: คิดราคาขายส่งเมล็ดกาแฟ

กติกา (ตามโจทย์):
1. ยอดดิบ = unit_price * qty (สตางค์)
2. ส่วนลดตามจำนวน (อัตราเดียว ไม่สะสม):
   - qty >= 50  -> ลด 7.5%
   - qty >= 10  -> ลด 3.5%
   - อื่น ๆ      -> ไม่ลด
3. ถ้า coupon = True ลดอีก 2.5% (คิดจากยอดที่เหลือหลังข้อ 2)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. ปัดครั้งเดียวตอนท้าย เป็นจำนวนเต็มสตางค์
   โจทย์ไม่ได้ระบุวิธีปัด -> ใช้ปัดครึ่งขึ้น (เงินที่ลูกค้าจ่ายเข้าร้าน)

ไม่มี side effect ตอน import. ตัวช่วยตรวจ input และปัดเศษคัดลอกมาจาก skills/money-arithmetic-rounding
และ skills/strict-input-validation เพื่อไม่ต้องพึ่ง sys.path.
"""

import math
from fractions import Fraction


# ---------- ตรวจข้อมูลนำเข้า ----------

def need_int(value, name, low=None, high=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


def need_bool(value, name):
    """flag: ต้องเป็น True หรือ False จริง"""
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


# ---------- ปัดเศษ ----------

def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


# ---------- อัตราที่ใช้ (exact) ----------

RATE_BULK_50 = Fraction(75, 1000)   # 7.5%
RATE_BULK_10 = Fraction(35, 1000)   # 3.5%
RATE_COUPON = Fraction(25, 1000)    # 2.5%
RATE_VAT = Fraction(7, 100)         # 7%


def bulk_discount_rate(qty):
    """อัตราส่วนลดตามจำนวนถุง (อัตราเดียว ไม่สะสม)"""
    if qty >= 50:
        return RATE_BULK_50
    if qty >= 10:
        return RATE_BULK_10
    return Fraction(0)


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    unit_price: ราคาต่อถุง (สตางค์, int, >= 0)
    qty:        จำนวนถุง (int, 1–1000)
    coupon:     True ถ้ามีคูปอง
    """
    need_int(unit_price, "unit_price", low=0)
    need_int(qty, "qty", low=1, high=1000)
    need_bool(coupon, "coupon")

    total = Fraction(unit_price) * qty                      # 1) ยอดดิบ ยังไม่ปัด
    total *= 1 - bulk_discount_rate(qty)                    # 2) ส่วนลดตามจำนวน
    if coupon:
        total *= 1 - RATE_COUPON                            # 3) คูปอง คิดจากยอดที่เหลือ
    total *= 1 + RATE_VAT                                   # 4) VAT ขั้นสุดท้าย
    return half_up(total)                                   # 5) ปัดครั้งเดียว


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน (หน่วยเป็นสตางค์)
    print(bulk_price(20000, 1, False))   # 200 บาท ซื้อ 1 ถุง
    print(bulk_price(20000, 10, True))
    print(bulk_price(20000, 50, True))
