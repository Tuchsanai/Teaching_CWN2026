import math
from fractions import Fraction

THRESHOLD = 50000  # 500 บาทในหน่วยสตางค์
BULK_DISCOUNT = Fraction(5, 100)
MEMBER_DISCOUNT = Fraction(10, 100)
VAT = Fraction(7, 100)


def to_frac(x):
    """แปลงตัวเลขเป็น Fraction ผ่าน str เพื่อไม่ให้คลาดเคลื่อนจาก float"""
    return Fraction(str(x))


def round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม ใช้ครั้งเดียวตอนคืนค่า"""
    return math.floor(f + Fraction(1, 2))


def _is_number(x):
    return isinstance(x, (int, float, Fraction)) and not isinstance(x, bool)


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    ลำดับการคิด:
    1. ยอดรวมก่อนลด = sum(price * qty)
    2. ถ้ายอดรวมก่อนลด >= 500 บาท ลด 5%
    3. ถ้า member = True ลดอีก 10% (คิดต่อจากยอดหลังข้อ 2)
    4. บวก VAT 7% ตอนท้าย
    5. ปัดครึ่งขึ้นครั้งเดียวที่ผลสุดท้าย
    """
    subtotal = Fraction(0)
    for item in items:
        price = item["price"]
        qty = item["qty"]
        if not _is_number(price) or price < 0:
            raise ValueError("price ต้องเป็นตัวเลขที่ไม่ติดลบ (สตางค์)")
        if isinstance(qty, bool) or not isinstance(qty, int) or qty < 1:
            raise ValueError("qty ต้องเป็นจำนวนเต็มตั้งแต่ 1")
        subtotal += to_frac(price) * qty

    total = subtotal
    if subtotal >= THRESHOLD:
        total *= 1 - BULK_DISCOUNT
    if member:
        total *= 1 - MEMBER_DISCOUNT
    total *= 1 + VAT

    return round_half_up(total)
