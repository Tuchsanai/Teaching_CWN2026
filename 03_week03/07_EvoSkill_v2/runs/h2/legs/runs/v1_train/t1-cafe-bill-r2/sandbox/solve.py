"""BaanKafe – คำนวณยอดที่ลูกค้าต้องจ่ายหน้าร้าน

กติกา (ทำตามลำดับ):
1. ยอดรวมก่อนลด = Σ(price × qty)  (หน่วย: สตางค์)
2. ยอดรวมตั้งแต่ 500 บาท (50,000 สตางค์) ขึ้นไป ลด 5%
3. ถ้าเป็นสมาชิก (member=True) ลดอีก 10% (คิดต่อจากยอดหลังข้อ 2)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. ปัดครึ่งขึ้น (half-up) เป็นจำนวนเต็มสตางค์ครั้งเดียวตอนคืนค่า
"""

import math
from fractions import Fraction

BAHT_THRESHOLD_SATANG = 50_000  # 500 บาท
DISCOUNT_RATE = Fraction(5, 100)
MEMBER_RATE = Fraction(10, 100)
VAT_RATE = Fraction(7, 100)


def _to_frac(x):
    """แปลงค่าตัวเลขเป็น Fraction โดยไม่เกิดคลาดเคลื่อนจาก float"""
    if isinstance(x, bool):
        raise ValueError(f"ค่าต้องเป็นตัวเลข ไม่ใช่ bool: {x!r}")
    if isinstance(x, (int, Fraction)):
        return Fraction(x)
    try:
        return Fraction(str(x))
    except (ValueError, TypeError, ZeroDivisionError):
        raise ValueError(f"ค่าไม่ใช่ตัวเลขที่ถูกต้อง: {x!r}") from None


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ยอดไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก
    """
    subtotal = Fraction(0)
    for item in items:
        price = _to_frac(item["price"])
        qty = _to_frac(item["qty"])
        if price < 0:
            raise ValueError(f"ราคาต้องไม่ติดลบ: {item['price']!r}")
        if qty < 1 or qty.denominator != 1:
            raise ValueError(f"จำนวนชิ้นต้องเป็นจำนวนเต็มตั้งแต่ 1: {item['qty']!r}")
        subtotal += price * qty

    total = subtotal

    # ข้อ 2: ลด 5% เมื่อยอดรวมก่อนลดตั้งแต่ 500 บาทขึ้นไป
    if subtotal >= BAHT_THRESHOLD_SATANG:
        total *= 1 - DISCOUNT_RATE

    # ข้อ 3: สมาชิกลดอีก 10% คิดต่อจากยอดหลังข้อ 2
    if member:
        total *= 1 - MEMBER_RATE

    # ข้อ 4: บวก VAT 7% เป็นขั้นสุดท้าย
    total *= 1 + VAT_RATE

    # ข้อ 5: ปัดครั้งเดียวที่ค่าที่คืน
    return _round_half_up(total)


if __name__ == "__main__":
    print(cafe_bill([{"price": 50_000, "qty": 1}], False))  # 50825
