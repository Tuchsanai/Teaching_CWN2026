import math
from fractions import Fraction

BULK_THRESHOLD = 50000              # 500 บาท (หน่วยสตางค์) ใช้ยอดก่อนหักส่วนลด
BULK_DISCOUNT = Fraction(5, 100)    # ลด 5%
MEMBER_DISCOUNT = Fraction(10, 100) # สมาชิกลดอีก 10% (คิดต่อเนื่อง)
VAT_RATE = Fraction(7, 100)         # VAT 7% เป็นขั้นสุดท้าย


def _to_int(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    f = Fraction(str(value))
    if f.denominator != 1:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    return int(f)


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    items: list ของ {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก
    """
    subtotal = 0
    for item in items:
        price = _to_int(item["price"], "price")
        qty = _to_int(item["qty"], "qty")
        if price < 0:
            raise ValueError("price ต้องไม่ติดลบ")
        if qty < 1:
            raise ValueError("qty ต้องมีค่าตั้งแต่ 1")
        subtotal += price * qty

    total = Fraction(subtotal)
    if subtotal >= BULK_THRESHOLD:
        total *= 1 - BULK_DISCOUNT
    if member:
        total *= 1 - MEMBER_DISCOUNT
    total *= 1 + VAT_RATE

    # ปัดครึ่งขึ้นครั้งเดียวที่ผลสุดท้าย
    return math.floor(total + Fraction(1, 2))
