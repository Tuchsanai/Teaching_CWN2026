import math
from decimal import Decimal
from fractions import Fraction


def to_frac(x):
    """รับได้ทั้ง int, float, Decimal โดยไม่เกิดคลาดเคลื่อนจาก float"""
    return Fraction(str(x))


def round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม ใช้ครั้งเดียวตอนคืนค่า (ยอดไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def _is_number(x):
    return isinstance(x, (int, float, Decimal)) and not isinstance(x, bool)


def cafe_bill(items, member):
    """คำนวณยอดที่ลูกค้าต้องจ่ายของ BaanKafe (หน่วยสตางค์, คืนค่าเป็น int)

    กติกาตามลำดับ:
    1. ยอดรวม = ผลรวม price * qty (สตางค์)
    2. ยอดรวมตั้งแต่ 500 บาท (50000 สตางค์) ขึ้นไป ลด 5%
    3. member = True ลดอีก 10% (คิดต่อเนื่องจากยอดหลังข้อ 2)
    4. บวก VAT 7% เป็นขั้นสุดท้าย
    5. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ครั้งเดียวตอนคืนค่า
    """
    total = Fraction(0)
    for item in items:
        price = item["price"]
        qty = item["qty"]
        if not _is_number(price) or price < 0:
            raise ValueError(f"price ไม่ถูกต้อง: {price!r}")
        if not _is_number(qty) or qty < 1 or to_frac(qty).denominator != 1:
            raise ValueError(f"qty ต้องเป็นจำนวนเต็มตั้งแต่ 1: {qty!r}")
        total += to_frac(price) * to_frac(qty)

    if total >= 50000:  # 500 บาท = 50000 สตางค์ (รวมค่าเท่ากับเกณฑ์)
        total *= Fraction(95, 100)

    if member:
        total *= Fraction(90, 100)

    total *= Fraction(107, 100)  # VAT 7%

    return round_half_up(total)
