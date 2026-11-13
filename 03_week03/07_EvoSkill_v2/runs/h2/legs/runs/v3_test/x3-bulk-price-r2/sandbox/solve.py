"""BaanKafe: คิดราคาขายส่งเมล็ดกาแฟ

กติกา (ทำตามลำดับนี้):
1. ยอดก่อนลด = unit_price (สตางค์/ถุง) × qty (ถุง)
2. ส่วนลดตามจำนวน (อัตราเดียว, ไม่สะสมกัน)
   - ซื้อ 50 ถุงขึ้นไป  ลด 7.5%
   - ซื้อ 10 ถุงขึ้นไป  ลด 3.5%
   - อื่น ๆ             ไม่ลด
3. ถ้ามีคูปอง (coupon=True) ลดอีก 2.5% คิดต่อจากยอดหลังข้อ 2
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. ปัดครึ่งขึ้น (half-up) ครั้งเดียวที่ผลสุดท้าย ได้จำนวนเต็มสตางค์

ไม่ใช้ float ในการคำนวณเงิน ใช้ fractions.Fraction ตลอดทาง
"""

import math
from fractions import Fraction

MIN_QTY = 1
MAX_QTY = 1000

VAT_RATE = Fraction(7, 100)
COUPON_RATE = Fraction(25, 1000)  # 2.5%

# (จำนวนถุงขั้นต่ำ, อัตราส่วนลด) เรียงจากมากไปน้อย
VOLUME_TIERS = (
    (50, Fraction(75, 1000)),  # 7.5%
    (10, Fraction(35, 1000)),  # 3.5%
)


def _to_fraction(x):
    """แปลงตัวเลขเป็น Fraction ผ่าน str เพื่อไม่ให้คลาดเคลื่อนจาก float"""
    if isinstance(x, bool):
        raise ValueError("ค่าต้องเป็นตัวเลข ไม่ใช่ bool")
    if isinstance(x, (int, Fraction)):
        return Fraction(x)
    try:
        return Fraction(str(x))
    except (TypeError, ValueError):
        raise ValueError(f"ค่าต้องเป็นตัวเลข: {x!r}") from None


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ยอดที่นี่ไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def _volume_discount_rate(qty):
    for min_qty, rate in VOLUME_TIERS:
        if qty >= min_qty:
            return rate
    return Fraction(0)


def bulk_price(unit_price, qty, coupon):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    unit_price: ราคาต่อถุง (สตางค์) ต้องไม่น้อยกว่า 0
    qty:        จำนวนถุง 1–1000
    coupon:     True = มีคูปองลดอีก 2.5%
    """
    price = _to_fraction(unit_price)
    if price < 0:
        raise ValueError("unit_price ต้องไม่ติดลบ")

    q = _to_fraction(qty)
    if q.denominator != 1:
        raise ValueError("qty ต้องเป็นจำนวนเต็ม")
    q = int(q)
    if not (MIN_QTY <= q <= MAX_QTY):
        raise ValueError(f"qty ต้องอยู่ระหว่าง {MIN_QTY}–{MAX_QTY}")

    if not isinstance(coupon, bool):
        raise ValueError("coupon ต้องเป็น True หรือ False")

    total = price * q

    # 2. ส่วนลดตามจำนวน (อัตราเดียว)
    total *= 1 - _volume_discount_rate(q)

    # 3. คูปองลดอีก คิดต่อจากยอดหลังส่วนลดข้อ 2
    if coupon:
        total *= 1 - COUPON_RATE

    # 4. VAT 7% เป็นขั้นสุดท้าย
    total *= 1 + VAT_RATE

    # 5. ปัดครั้งเดียว
    return _round_half_up(total)


if __name__ == "__main__":
    print(bulk_price(10000, 50, True))
