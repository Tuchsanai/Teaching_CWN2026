"""BaanKafe bulk coffee-bean pricing.

ราคาคิดเป็นสตางค์ทั้งหมด ผลลัพธ์เป็นจำนวนเต็มสตางค์
"""

import math
from fractions import Fraction

VAT_RATE = Fraction(7, 100)           # VAT 7% (ขั้นสุดท้าย)
COUPON_RATE = Fraction(25, 1000)      # คูปองลดอีก 2.5%
MAX_QTY = 1000


def _bulk_rate(qty: int) -> Fraction:
    """อัตราส่วนลดตามจำนวนถุง (ใช้อัตราเดียว ไม่สะสม)."""
    if qty >= 50:
        return Fraction(75, 1000)     # 7.5%
    if qty >= 10:
        return Fraction(35, 1000)     # 3.5%
    return Fraction(0)


def bulk_price(unit_price: int, qty: int, coupon: bool) -> int:
    """คืนยอดที่ลูกค้าต้องจ่าย (สตางค์, จำนวนเต็ม)

    ลำดับการคิด:
      1. subtotal = unit_price * qty
      2. ลดตามจำนวนถุง (ขั้นบันได 10 ถุง = 3.5%, 50 ถุง = 7.5%)
      3. ถ้ามีคูปอง ลดอีก 2.5% จากยอดหลังลดข้อ 2
      4. บวก VAT 7% จากยอดหลังลดทั้งหมด
      5. ปัดเศษครึ่งขึ้นเป็นสตางค์

    ไม่ทำการปัดเศษระหว่างขั้น เพื่อไม่ให้เกิดความคลาดเคลื่อนสะสม
    """
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise TypeError("unit_price ต้องเป็นจำนวนเต็ม (สตางค์)")
    if unit_price < 0:
        raise ValueError("unit_price ต้องไม่ติดลบ")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise TypeError("qty ต้องเป็นจำนวนเต็ม")
    if not 1 <= qty <= MAX_QTY:
        raise ValueError(f"qty ต้องอยู่ระหว่าง 1 ถึง {MAX_QTY}")
    if not isinstance(coupon, bool):
        raise TypeError("coupon ต้องเป็น True หรือ False")

    subtotal = Fraction(unit_price * qty)
    after_bulk = subtotal * (1 - _bulk_rate(qty))
    after_coupon = after_bulk * (1 - COUPON_RATE) if coupon else after_bulk
    with_vat = after_coupon * (1 + VAT_RATE)

    # ปัดเศษครึ่งขึ้น (ค่าไม่ติดลบ)
    return math.floor(with_vat + Fraction(1, 2))


if __name__ == "__main__":
    print(bulk_price(12000, 1, False))   # ตัวอย่าง: 1 ถุง 120 บาท
    print(bulk_price(12000, 10, False))  # 10 ถุง ลด 3.5%
    print(bulk_price(12000, 50, True))   # 50 ถุง ลด 7.5% + คูปอง 2.5%
