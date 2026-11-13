"""BaanKafe bulk coffee-bean pricing.

ราคาทั้งหมดเป็นสตางค์ (จำนวนเต็ม) การคำนวณใช้ Fraction เพื่อไม่ให้เกิด
ข้อผิดพลาดจากเลขทศนิยม แล้วปัดเศษ "ครั้งเดียว" ตอนท้ายแบบปัดขึ้นเมื่อ .5 (half-up)

ลำดับการคิด
1. ราคารวม = unit_price * qty
2. ส่วนลดขายส่ง (ใช้อัตราเดียว): qty >= 50 ลด 7.5%, qty >= 10 ลด 3.5%
3. ถ้ามีคูปอง ลดเพิ่มอีก 2.5% จากยอดหลังลดขายส่ง (ลดแบบต่อเนื่อง ไม่บวกอัตราเข้าด้วยกัน)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. ปัดเป็นจำนวนเต็มสตางค์
"""

import math
from fractions import Fraction

BULK_TIER_50 = Fraction(75, 1000)  # 7.5%
BULK_TIER_10 = Fraction(35, 1000)  # 3.5%
COUPON_RATE = Fraction(25, 1000)   # 2.5%
VAT_RATE = Fraction(7, 100)        # 7%


def _is_int(value):
    # bool เป็น subclass ของ int ใน Python จึงต้องกันไว้ต่างหาก
    return isinstance(value, int) and not isinstance(value, bool)


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่าย (สตางค์ จำนวนเต็ม)

    unit_price: ราคาต่อถุง (สตางค์, >= 0)
    qty: จำนวนถุง (1 ถึง 1000)
    coupon: True ถ้ามีคูปอง
    """
    if not _is_int(unit_price) or unit_price < 0:
        raise ValueError("unit_price ต้องเป็นจำนวนเต็มสตางค์ที่ >= 0")
    if not _is_int(qty) or not (1 <= qty <= 1000):
        raise ValueError("qty ต้องเป็นจำนวนเต็มระหว่าง 1 ถึง 1000")
    if not isinstance(coupon, bool):
        raise ValueError("coupon ต้องเป็น True หรือ False")

    if qty >= 50:
        bulk_rate = BULK_TIER_50
    elif qty >= 10:
        bulk_rate = BULK_TIER_10
    else:
        bulk_rate = Fraction(0)

    total = Fraction(unit_price * qty) * (1 - bulk_rate)

    if coupon:
        total *= 1 - COUPON_RATE

    total *= 1 + VAT_RATE

    # ปัดเป็นจำนวนเต็มสตางค์แบบ half-up (ไม่มีค่าติดลบ จึงใช้ floor(x + 1/2) ได้)
    return math.floor(total + Fraction(1, 2))


if __name__ == "__main__":
    # ตัวอย่างการใช้งานและการตรวจสอบเบื้องต้น
    assert bulk_price(10000, 1, False) == 10700      # 100 บาท ไม่ลด + VAT
    assert bulk_price(10000, 10, False) == 103255    # ลด 3.5% + VAT
    assert bulk_price(10000, 50, False) == 494875    # 500,000 ลด 7.5% + VAT
    assert bulk_price(10000, 10, True) == 100674     # 100,000 ลด 3.5% -> คูปอง 2.5% -> VAT (100673.625 ปัดขึ้น)
    assert bulk_price(0, 1000, True) == 0
    print("ok")
