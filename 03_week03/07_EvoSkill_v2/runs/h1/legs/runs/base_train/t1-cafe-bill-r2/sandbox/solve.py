from fractions import Fraction
from math import floor

BAHT = 100                 # 1 บาท = 100 สตางค์
BULK_THRESHOLD = 500 * BAHT  # ยอดรวมตั้งแต่ 500 บาท (หน่วยสตางค์)
BULK_RATE = Fraction(5, 100)
MEMBER_RATE = Fraction(10, 100)
VAT_RATE = Fraction(7, 100)


def cafe_bill(items, member):
    """คำนวณยอดที่ลูกค้าต้องจ่าย (หน่วยสตางค์ เป็นจำนวนเต็ม)

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก (ลดเพิ่ม 10%)

    ลำดับการคิด:
      1. ยอดรวม = sum(price * qty)
      2. ถ้ายอดรวม >= 500 บาท ลด 5%
      3. ถ้า member ลดอีก 10% (ทบจากยอดหลังขั้นที่ 2)
      4. บวก VAT 7% เป็นขั้นสุดท้าย
      5. ปัดเศษครึ่งขึ้นให้เป็นจำนวนเต็มสตางค์
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

    # ใช้ Fraction เพื่อหลีกเลี่ยงความคลาดเคลื่อนของทศนิยม (floating point)
    total = Fraction(subtotal)

    if subtotal >= BULK_THRESHOLD:
        total *= 1 - BULK_RATE

    if member:
        total *= 1 - MEMBER_RATE

    total *= 1 + VAT_RATE

    # ปัดเศษครึ่งขึ้น (round half up) เป็นจำนวนเต็มสตางค์
    return floor(total + Fraction(1, 2))


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    sample = [{"price": 6000, "qty": 2}, {"price": 4500, "qty": 1}]  # 165 บาท
    print(cafe_bill(sample, False))
    big = [{"price": 15000, "qty": 4}]  # 600 บาท
    print(cafe_bill(big, True))
