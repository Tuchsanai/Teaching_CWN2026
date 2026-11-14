from fractions import Fraction
from math import floor

BULK_THRESHOLD = 50_000   # 500 บาท ในหน่วยสตางค์
BULK_DISCOUNT = Fraction(5, 100)
MEMBER_DISCOUNT = Fraction(10, 100)
VAT_RATE = Fraction(7, 100)


def cafe_bill(items, member):
    """คำนวณยอดที่ลูกค้าต้องจ่าย (จำนวนเต็มสตางค์)

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก
    """
    subtotal = sum(int(it["price"]) * int(it["qty"]) for it in items)

    total = Fraction(subtotal)
    if subtotal >= BULK_THRESHOLD:
        total *= 1 - BULK_DISCOUNT
    if member:
        total *= 1 - MEMBER_DISCOUNT
    total *= 1 + VAT_RATE

    # ปัดเศษแบบ half-up ให้เป็นจำนวนเต็มสตางค์ (คำนวณด้วย Fraction ไม่มีค่าคลาดเคลื่อนจาก float)
    return floor(total + Fraction(1, 2))


if __name__ == "__main__":
    print(cafe_bill([{"price": 10_000, "qty": 3}], False))  # 300 บาท -> 321 บาท
    print(cafe_bill([{"price": 25_000, "qty": 2}], False))  # 500 บาท -> 500*0.95*1.07 = 50825
    print(cafe_bill([{"price": 25_000, "qty": 2}], True))   # 500 บาท, สมาชิก
