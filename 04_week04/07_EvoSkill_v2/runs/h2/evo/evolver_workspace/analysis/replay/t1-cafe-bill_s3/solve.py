from fractions import Fraction
import math

# หน่วยทั้งหมดเป็นสตางค์ (1 บาท = 100 สตางค์)
DISCOUNT_THRESHOLD = 500 * 100  # ยอดรวมตั้งแต่ 500 บาทขึ้นไป
BULK_DISCOUNT = Fraction(5, 100)  # ลด 5%
MEMBER_DISCOUNT = Fraction(10, 100)  # สมาชิกลดอีก 10%
VAT_RATE = Fraction(7, 100)  # VAT 7%


def cafe_bill(items, member):
    """คำนวณยอดที่ลูกค้าต้องจ่าย (สตางค์, จำนวนเต็ม)

    items: list ของ {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก

    ลำดับการคิด:
      1. ยอดรวม = sum(price * qty)
      2. ถ้ายอดรวม >= 500 บาท ลด 5%
      3. ถ้าเป็นสมาชิก ลดอีก 10% (คิดจากยอดหลังขั้นที่ 2)
      4. บวก VAT 7% (ขั้นสุดท้าย)
    ใช้ Fraction เพื่อไม่ให้เกิด error ของทศนิยม แล้วปัดเศษครึ่งขึ้นเป็นสตางค์
    """
    subtotal = sum(Fraction(item["price"]) * Fraction(item["qty"]) for item in items)

    total = subtotal
    if subtotal >= DISCOUNT_THRESHOLD:
        total *= 1 - BULK_DISCOUNT
    if member:
        total *= 1 - MEMBER_DISCOUNT
    total *= 1 + VAT_RATE

    # ปัดเศษครึ่งขึ้น (ยอดเป็นบวกเสมอ)
    return math.floor(total + Fraction(1, 2))
