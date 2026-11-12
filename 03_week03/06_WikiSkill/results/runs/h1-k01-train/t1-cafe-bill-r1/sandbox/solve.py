"""BaanKafe: คำนวณยอดเงินที่ลูกค้าต้องจ่ายหน้าร้าน

ราคาทั้งหมดเป็นสตางค์ (จำนวนเต็ม) เพื่อหลีกเลี่ยงปัญหาทศนิยมของ float
"""

from fractions import Fraction
from math import floor

BULK_THRESHOLD = 50_000  # 500 บาท = 50,000 สตางค์
BULK_DISCOUNT = Fraction(5, 100)  # ลด 5%
MEMBER_DISCOUNT = Fraction(10, 100)  # ลดเพิ่ม 10% สำหรับสมาชิก
VAT_RATE = Fraction(7, 100)  # VAT 7%


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นสตางค์ (จำนวนเต็ม)

    items  : list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member : True ถ้าเป็นสมาชิก (ลดเพิ่ม 10%)

    ลำดับการคิด:
      1. รวมยอดสินค้า
      2. ถ้ายอดรวม>= 500 บาท ลด 5%
      3. ถ้าเป็นสมาชิก ลดอีก 10% (คิดจากยอดหลังลดข้อ 2)
      4. บวก VAT 7% (ขั้นสุดท้าย)
      5. ปัดเศษเป็นจำนวนเต็มสตางค์ (ปัดขึ้นเมื่อ .5 ขึ้นไป)

    >>> cafe_bill([{"price": 10000, "qty": 5}], False)  # 500 บาท -> 500*0.95*1.07
    50825
    >>> cafe_bill([{"price": 10000, "qty": 5}], True)
    45743
    >>> cafe_bill([{"price": 4550, "qty": 1}], False)  # ต่ำกว่า 500 บาท ไม่ลด
    4869
    """
    subtotal = 0
    for item in items:
        price = int(item["price"])
        qty = int(item["qty"])
        if price < 0:
            raise ValueError("price ต้องไม่ติดลบ")
        if qty < 1:
            raise ValueError("qty ต้องอย่างน้อย 1")
        subtotal += price * qty

    total = Fraction(subtotal)
    if subtotal >= BULK_THRESHOLD:
        total *= 1 - BULK_DISCOUNT
    if member:
        total *= 1 - MEMBER_DISCOUNT
    total *= 1 + VAT_RATE

    # ปัดครึ่งขึ้น (half-up) โดยใช้เลขเศษส่วน ไม่มีความคลาดเคลื่อนจาก float
    return floor(total + Fraction(1, 2))


if __name__ == "__main__":
    import doctest

    doctest.testmod()
