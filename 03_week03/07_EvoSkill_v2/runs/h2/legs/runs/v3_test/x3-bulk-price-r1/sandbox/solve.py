"""ร้าน BaanKafe: คิดราคาขายส่งเมล็ดกาแฟ

หน่วยทั้งหมดเป็นสตางค์ ผลลัพธ์เป็นจำนวนเต็มสตางค์

กติกาตามลำดับ:
1. ยอดก่อนลด = unit_price * qty
2. ส่วนลดตามจำนวน (อัตราเดียว ไม่สะสม):
   - qty >= 50 ลด 7.5%
   - qty >= 10 ลด 3.5%
   - อื่น ๆ ไม่ลด
3. ถ้า coupon เป็น True ลดอีก 2.5% (คิดต่อจากยอดหลังข้อ 2)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. ปัดครึ่งขึ้นครั้งเดียวที่ยอดสุดท้าย
"""

import math
from fractions import Fraction

BULK_TIER_50 = (50, Fraction(75, 1000))  # ซื้อ 50 ถุงขึ้นไป ลด 7.5%
BULK_TIER_10 = (10, Fraction(35, 1000))  # ซื้อ 10 ถุงขึ้นไป ลด 3.5%
COUPON_RATE = Fraction(25, 1000)         # คูปอง ลด 2.5%
VAT_RATE = Fraction(7, 100)              # VAT 7%


def _to_frac(x):
    """แปลงเป็น Fraction ผ่าน str เพื่อหลีกเลี่ยงค่าคลาดเคลื่อนจาก float"""
    return Fraction(str(x))


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ยอดไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def _bulk_rate(qty):
    if qty >= BULK_TIER_50[0]:
        return BULK_TIER_50[1]
    if qty >= BULK_TIER_10[0]:
        return BULK_TIER_10[1]
    return Fraction(0)


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่าย (สตางค์, int)

    unit_price: ราคาต่อถุง (สตางค์) ตั้งแต่ 0
    qty: จำนวนถุง 1–1000
    coupon: True = มีคูปอง
    """
    if isinstance(unit_price, bool) or isinstance(qty, bool):
        raise ValueError("unit_price และ qty ต้องเป็นตัวเลข ไม่ใช่ bool")

    price = _to_frac(unit_price)
    if price < 0:
        raise ValueError("unit_price ต้องไม่ติดลบ")

    count = _to_frac(qty)
    if count.denominator != 1 or not (1 <= count <= 1000):
        raise ValueError("qty ต้องเป็นจำนวนเต็มในช่วง 1–1000")
    qty_int = int(count)

    total = price * qty_int                             # 1. ยอดก่อนลด
    total *= 1 - _bulk_rate(qty_int)                    # 2. ลดตามจำนวน
    if coupon:
        total *= 1 - COUPON_RATE                        # 3. คูปอง (ต่อจากข้อ 2)
    total *= 1 + VAT_RATE                               # 4. VAT

    return _round_half_up(total)                        # 5. ปัดครั้งเดียว


if __name__ == "__main__":
    print(bulk_price(10000, 10, False))   # 103255
    print(bulk_price(10000, 50, True))    # 482503
