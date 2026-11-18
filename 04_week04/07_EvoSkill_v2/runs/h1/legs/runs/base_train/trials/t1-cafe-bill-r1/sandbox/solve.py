"""BaanKafe checkout: คำนวณยอดที่ลูกค้าต้องจ่าย

หน่วยทั้งหมดเป็นสตางค์ (จำนวนเต็ม) เพื่อหลีกเลี่ยงปัญหา floating point
ลำดับการคิด:
    1. ยอดรวม = sum(price * qty)
    2. ถ้ายอดรวม >= 500 บาท (50,000 สตางค์) ลด 5%
    3. ถ้าเป็นสมาชิก ลดอีก 10% (คิดต่อจากยอดหลังขั้นที่ 2)
    4. บวก VAT 7% เป็นขั้นสุดท้าย
    5. ปัดเศษครั้งเดียวที่ท้ายสุด (ปัดขึ้นเมื่อ .5 ขึ้นไป) ให้เป็นสตางค์จำนวนเต็ม
"""

from fractions import Fraction
from decimal import Decimal, ROUND_HALF_UP

THRESHOLD_SATANG = 500 * 100  # 500 บาท
BULK_DISCOUNT = Fraction(5, 100)
MEMBER_DISCOUNT = Fraction(10, 100)
VAT_RATE = Fraction(7, 100)


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก
    """
    subtotal = 0
    for item in items:
        price = int(item["price"])
        qty = int(item["qty"])
        if price < 0:
            raise ValueError("price must not be negative")
        if qty < 1:
            raise ValueError("qty must be at least 1")
        subtotal += price * qty

    total = Fraction(subtotal)

    if subtotal >= THRESHOLD_SATANG:
        total *= 1 - BULK_DISCOUNT

    if member:
        total *= 1 - MEMBER_DISCOUNT

    total *= 1 + VAT_RATE

    # ปัดครึ่งขึ้นเป็นสตางค์จำนวนเต็ม (ทำครั้งเดียวตอนท้าย)
    rounded = Decimal(total.numerator) / Decimal(total.denominator)
    return int(rounded.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    sample = [{"price": 15000, "qty": 2}, {"price": 7000, "qty": 1}]  # 370 บาท
    print(cafe_bill(sample, False))  # ไม่ถึง 500 บาท ไม่ลด -> 39,590 สตางค์
    print(cafe_bill(sample, True))
