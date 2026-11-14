"""BaanKafe: คิดเงินหน้าร้าน

หน่วยทั้งหมดเป็นสตางค์ (1 บาท = 100 สตางค์) คำนวณด้วย Fraction
แล้วปัดครึ่งขึ้นครั้งเดียวที่ขั้นสุดท้าย

ลำดับการคิด:
  1. ยอดรวม = sum(price * qty)
  2. ถ้ายอดรวม >= 50,000 สตางค์ (500 บาท) ลด 5% บนยอดรวม
  3. ถ้า member ลดอีก 10% บนยอดที่เหลือจากข้อ 2 (ต่อเนื่อง ไม่ใช่รวมเป็น 15%)
  4. บวก VAT 7% บนยอดหลังส่วนลดทั้งหมด (ขั้นสุดท้าย)
  5. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์
"""

import math
from fractions import Fraction

DISCOUNT_THRESHOLD = 50_000  # 500 บาท ในหน่วยสตางค์
BULK_DISCOUNT_PCT = 5
MEMBER_DISCOUNT_PCT = 10
VAT_PCT = 7


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์ (int)"""
    subtotal = sum(item["price"] * item["qty"] for item in items)

    total = Fraction(subtotal)

    # ข้อ 2: ลด 5% เมื่อยอดตั้งต้นตั้งแต่ 500 บาทขึ้นไป
    if subtotal >= DISCOUNT_THRESHOLD:
        total *= Fraction(100 - BULK_DISCOUNT_PCT, 100)

    # ข้อ 3: สมาชิกลดอีก 10% บนยอดที่เหลือ
    if member:
        total *= Fraction(100 - MEMBER_DISCOUNT_PCT, 100)

    # ข้อ 4: VAT 7% ขั้นสุดท้าย
    total *= Fraction(100 + VAT_PCT, 100)

    # ข้อ 5: ปัดครึ่งขึ้นครั้งเดียว (ค่าไม่ติดลบ)
    return math.floor(total + Fraction(1, 2))
