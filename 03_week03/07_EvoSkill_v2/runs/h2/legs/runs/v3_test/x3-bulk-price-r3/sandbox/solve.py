"""BaanKafe: คิดราคาขายส่งเมล็ดกาแฟ (หน่วยเป็นสตางค์)

ลำดับการคิด (คิดต่อเนื่องจากยอดที่เหลือ ไม่บวกอัตรารวมกัน):
  1. ยอดรวม = unit_price * qty
  2. ส่วนลดตามจำนวน: qty >= 50 ลด 7.5%, qty >= 10 ลด 3.5% (ใช้อัตราเดียวตามขั้นสูงสุดที่เข้าเงื่อนไข)
  3. ถ้ามีคูปอง ลดอีก 2.5% จากยอดหลังข้อ 2
  4. บวก VAT 7% เป็นขั้นสุดท้าย
  5. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ครั้งเดียวที่ผลสุดท้าย
"""

from fractions import Fraction
import math


def _to_frac(x):
    """แปลงตัวเลขเป็น Fraction ผ่าน str เพื่อไม่ให้เกิดความคลาดเคลื่อนของ float"""
    return Fraction(str(x))


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ใช้กับยอดที่ไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def _bulk_rate(qty):
    """อัตราส่วนลดตามจำนวนถุง (ใช้อัตราเดียวตามขั้นสูงสุดที่เข้าเงื่อนไข)"""
    if qty >= 50:
        return Fraction(75, 1000)  # 7.5%
    if qty >= 10:
        return Fraction(35, 1000)  # 3.5%
    return Fraction(0)


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์

    unit_price: ราคาต่อถุง (สตางค์, >= 0)
    qty:        จำนวนถุง (1–1000)
    coupon:     True ถ้ามีคูปอง
    """
    if isinstance(unit_price, bool) or isinstance(qty, bool):
        raise ValueError("unit_price และ qty ต้องเป็นตัวเลข")

    price = _to_frac(unit_price)
    if price < 0:
        raise ValueError("unit_price ต้องไม่ติดลบ")

    q = _to_frac(qty)
    if q.denominator != 1 or not (1 <= q <= 1000):
        raise ValueError("qty ต้องเป็นจำนวนเต็มระหว่าง 1 ถึง 1000")
    qty_int = int(q)

    if price.denominator != 1:
        raise ValueError("unit_price ต้องเป็นจำนวนเต็มสตางค์")

    subtotal = price * qty_int
    after_bulk = subtotal * (1 - _bulk_rate(qty_int))
    after_coupon = after_bulk * (1 - Fraction(25, 1000)) if coupon else after_bulk
    total = after_coupon * (1 + Fraction(7, 100))  # VAT 7%

    return _round_half_up(total)


if __name__ == "__main__":
    print(bulk_price(10000, 1, False))
    print(bulk_price(10000, 10, False))
    print(bulk_price(10000, 50, True))
