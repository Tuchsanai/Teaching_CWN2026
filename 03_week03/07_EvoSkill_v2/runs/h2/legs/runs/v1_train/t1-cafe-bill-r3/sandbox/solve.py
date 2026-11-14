"""BaanKafe: คิดเงินหน้าร้าน

หน่วยทั้งหมดเป็นสตางค์ (1 บาท = 100 สตางค์) และคำนวณด้วย Fraction
ปัดเศษครั้งเดียวที่ขั้นสุดท้าย (ปัดครึ่งขึ้น)

ลำดับการคิด:
1. ยอดรวม = sum(price * qty)
2. ถ้ายอดรวม >= 500 บาท (50000 สตางค์) ลด 5% บนยอดรวม
3. ถ้า member = True ลดอีก 10% บนยอดที่เหลือจากขั้นที่ 2 (ต่อเนื่อง ไม่ใช่รวมเป็น 15%)
4. บวก VAT 7% บนยอดหลังส่วนลดทั้งหมด (ขั้นสุดท้าย)
5. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์
"""

import math
from fractions import Fraction

BULK_THRESHOLD_SATANG = 50000  # 500 บาท
BULK_DISCOUNT_PCT = 5
MEMBER_DISCOUNT_PCT = 10
VAT_PCT = 7


def _round_half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ค่าไม่ติดลบ)"""
    return math.floor(x + Fraction(1, 2))


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย (จำนวนเต็มสตางค์)

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก
    """
    subtotal = 0
    for item in items:
        price = item["price"]
        qty = item["qty"]
        if price < 0:
            raise ValueError("price ต้องไม่ติดลบ")
        if qty < 1:
            raise ValueError("qty ต้องอย่างน้อย 1")
        subtotal += price * qty

    total = Fraction(subtotal)

    if subtotal >= BULK_THRESHOLD_SATANG:
        total *= Fraction(100 - BULK_DISCOUNT_PCT, 100)

    if member:
        total *= Fraction(100 - MEMBER_DISCOUNT_PCT, 100)

    total *= Fraction(100 + VAT_PCT, 100)

    return int(_round_half_up(total))


if __name__ == "__main__":
    # ตัวอย่าง: กาแฟ 60 บาท x 10 แก้ว (ยอด 600 บาท), สมาชิก
    print(cafe_bill([{"price": 6000, "qty": 10}], True))  # 54891 สตางค์ = 548.91 บาท
