"""BaanKafe — คำนวณยอดเงินที่ลูกค้าต้องจ่ายหน้าร้าน

กติกา:
1. ยอดรวม = ผลรวม (price * qty) หน่วยเป็นสตางค์
2. ถ้ายอดรวมตั้งแต่ 500 บาท (50,000 สตางค์) ขึ้นไป ลด 5%
3. ถ้าเป็นสมาชิก (member=True) ลดอีก 10% (คิดต่อจากยอดหลังลดข้อ 2)
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. คืนยอดที่ต้องจ่ายเป็นจำนวนเต็มสตางค์ (ปัดทศนิยมแบบ half-up)

ใช้ Fraction เพื่อให้การคำนวณเป็นทศนิยมที่แม่นยำ ไม่มี error จาก float
"""

from fractions import Fraction

BULK_THRESHOLD_SATANG = 50_000  # 500 บาท
BULK_DISCOUNT = Fraction(5, 100)
MEMBER_DISCOUNT = Fraction(10, 100)
VAT_RATE = Fraction(7, 100)


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก
    """
    subtotal = sum(int(it["price"]) * int(it["qty"]) for it in items)

    total = Fraction(subtotal)

    # ขั้นที่ 2: ลด 5% เมื่อยอดรวมตั้งแต่ 500 บาทขึ้นไป
    if subtotal >= BULK_THRESHOLD_SATANG:
        total *= 1 - BULK_DISCOUNT

    # ขั้นที่ 3: ลดเพิ่ม 10% สำหรับสมาชิก
    if member:
        total *= 1 - MEMBER_DISCOUNT

    # ขั้นที่ 4: VAT 7% (ขั้นสุดท้าย)
    total *= 1 + VAT_RATE

    # ขั้นที่ 5: ปัดเป็นจำนวนเต็มสตางค์ (half-up, ค่าไม่ติดลบ)
    return int(total + Fraction(1, 2))


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(cafe_bill([{"price": 10_000, "qty": 2}], False))  # 200 บาท -> 214 บาท = 21400
    print(cafe_bill([{"price": 25_000, "qty": 2}], False))  # 500 บาท -> ลด 5% -> VAT
    print(cafe_bill([{"price": 25_000, "qty": 2}], True))   # ลด 5% + 10% + VAT
