"""BaanKafe: คำนวณยอดเงินที่ลูกค้าต้องจ่ายหน้าร้าน

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม) เพื่อหลีกเลี่ยงปัญหาทศนิยมของ float
ลำดับการคิด:
    1. ยอดรวม = ผลรวม(price * qty)
    2. ถ้ายอดรวม >= 500 บาท (50000 สตางค์) ลด 5%
    3. ถ้า member = True ลดอีก 10% (ลดต่อจากยอดหลังขั้นที่ 2)
    4. บวก VAT 7% เป็นขั้นสุดท้าย
    5. ปัดเศษครึ่งขึ้นให้เป็นจำนวนเต็มสตางค์
"""

from fractions import Fraction
import math

THRESHOLD_SATANG = 50_000  # 500 บาท
DISCOUNT_BULK = Fraction(95, 100)     # ลด 5%
DISCOUNT_MEMBER = Fraction(90, 100)   # ลด 10%
VAT_MULTIPLIER = Fraction(107, 100)   # VAT 7%


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย (สตางค์, จำนวนเต็ม)

    items: list ของ dict {"price": ราคาต่อชิ้นเป็นสตางค์, "qty": จำนวนชิ้น >= 1}
    member: True ถ้าเป็นสมาชิก
    """
    subtotal = sum(int(item["price"]) * int(item["qty"]) for item in items)

    total = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:
        total *= DISCOUNT_BULK
    if member:
        total *= DISCOUNT_MEMBER
    total *= VAT_MULTIPLIER

    # ปัดเศษครึ่งขึ้นเป็นสตางค์ (floor(x + 1/2))
    return math.floor(total + Fraction(1, 2))


if __name__ == "__main__":
    sample = [{"price": 30_000, "qty": 2}]  # 2 แก้ว x 300 บาท = 600 บาท
    print(cafe_bill(sample, member=True))   # 54891 สตางค์ = 548.91 บาท
