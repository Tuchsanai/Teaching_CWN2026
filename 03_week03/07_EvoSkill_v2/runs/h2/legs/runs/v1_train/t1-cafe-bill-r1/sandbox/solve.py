import math
from fractions import Fraction

THRESHOLD = Fraction(50000)          # 500 บาท เป็นสตางค์
DISCOUNT_BULK = Fraction(5, 100)     # ลด 5% เมื่อยอดรวม >= 500 บาท
DISCOUNT_MEMBER = Fraction(10, 100)  # สมาชิกลดอีก 10%
VAT = Fraction(7, 100)               # VAT 7% ขั้นสุดท้าย


def to_frac(x):
    """รับได้ทั้ง int, float, Decimal โดยไม่เกิดคลาดเคลื่อนจาก float"""
    return Fraction(str(x))


def round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม ใช้ครั้งเดียวตอนคืนค่า"""
    return math.floor(f + Fraction(1, 2))


def cafe_bill(items, member=False):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    ลำดับการคิด:
      1. ยอดรวม = sum(price * qty) (สตางค์)
      2. ถ้ายอดรวม >= 500 บาท ลด 5%
      3. ถ้า member = True ลดอีก 10% (คูณต่อจากข้อ 2)
      4. บวก VAT 7% (คูณด้วย 1.07)
      5. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ครั้งเดียวที่ค่าที่คืน
    """
    subtotal = Fraction(0)
    for item in items:
        price = item["price"]
        qty = item["qty"]
        if isinstance(qty, bool) or to_frac(qty) < 1:
            raise ValueError("qty ต้องเป็นจำนวนเต็มตั้งแต่ 1")
        subtotal += to_frac(price) * to_frac(qty)

    total = subtotal
    if subtotal >= THRESHOLD:
        total *= 1 - DISCOUNT_BULK
    if member:
        total *= 1 - DISCOUNT_MEMBER
    total *= 1 + VAT

    return round_half_up(total)


if __name__ == "__main__":
    # ตัวอย่าง: กาแฟ 3 แก้ว ราคา 150 บาท (15000 สตางค์) + เค้ก 2 ชิ้น ราคา 100 บาท (10000 สตางค์)
    # ยอดรวม 65000 สตางค์ (650 บาท) >= 500 บาท -> ลด 5% -> 61750 -> VAT 7% -> 66072.5 -> 66073 สตางค์
    sample = [
        {"price": 15000, "qty": 3},
        {"price": 10000, "qty": 2},
    ]
    print(cafe_bill(sample, member=False))
    print(cafe_bill(sample, member=True))
