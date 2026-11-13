"""BaanKafe: คิดเงินหน้าร้าน

กติกา (ทำตามลำดับ โดยคูณต่อเนื่องกับยอดก่อนหน้า):
  1. ยอดรวม = sum(price * qty) หน่วยสตางค์
  2. ถ้ายอดรวม >= 50,000 สตางค์ (500 บาท) ลด 5%
  3. ถ้า member = True ลดอีก 10% (จากยอดหลังข้อ 2)
  4. บวก VAT 7% เป็นขั้นสุดท้าย
  ปัดครึ่งขึ้น (half-up) เป็นจำนวนเต็มสตางค์ครั้งเดียวตอนคืนค่า
"""

import math
from fractions import Fraction

THRESHOLD_SATANG = 50_000  # 500 บาท
DISCOUNT_BULK = Fraction(5, 100)
DISCOUNT_MEMBER = Fraction(10, 100)
VAT = Fraction(7, 100)


def _to_int(x, name):
    """รับ int หรือ float/Decimal ที่เป็นจำนวนเต็มพอดี แล้วคืนเป็น int"""
    if isinstance(x, bool):
        raise ValueError(f"{name} ต้องเป็นตัวเลข ไม่ใช่ bool")
    f = Fraction(str(x))
    if f.denominator != 1:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็มสตางค์: {x!r}")
    return int(f)


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ยอดไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย (จำนวนเต็มสตางค์)

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก
    """
    subtotal = 0
    for it in items:
        price = _to_int(it["price"], "price")
        qty = _to_int(it["qty"], "qty")
        if price < 0:
            raise ValueError(f"price ต้องไม่ติดลบ: {price}")
        if qty < 1:
            raise ValueError(f"qty ต้องตั้งแต่ 1 ขึ้นไป: {qty}")
        subtotal += price * qty

    total = Fraction(subtotal)

    # ข้อ 2: ยอดรวมตั้งแต่ 500 บาทขึ้นไป ลด 5%
    if subtotal >= THRESHOLD_SATANG:
        total *= 1 - DISCOUNT_BULK

    # ข้อ 3: สมาชิกลดอีก 10% (คูณต่อจากข้อ 2)
    if member:
        total *= 1 - DISCOUNT_MEMBER

    # ข้อ 4: บวก VAT 7% ขั้นสุดท้าย
    total *= 1 + VAT

    # ปัดครั้งเดียวที่ค่าที่คืน
    return _round_half_up(total)


if __name__ == "__main__":
    demo = [{"price": 25_000, "qty": 2}, {"price": 10_000, "qty": 1}]
    print(cafe_bill(demo, False))
    print(cafe_bill(demo, True))
