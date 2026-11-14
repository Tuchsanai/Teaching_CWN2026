"""BaanKafe: คิดเงินหน้าร้าน

กติกา (ทำตามลำดับนี้ทุกข้อ):
1. ยอดรวมก่อนลด = sum(price * qty)  (หน่วยสตางค์)
2. ยอดรวม >= 50,000 สตางค์ (500 บาท) ลด 5%
3. member = True ลดอีก 10% (คิดบนยอดที่เหลือหลังข้อ 2)
4. บวก VAT 7% ที่ขั้นสุดท้าย (คิดบนยอดหลังส่วนลดทั้งหมด)
5. ปัดเศษครั้งเดียวที่ขั้นสุดท้าย: ปัดลง (ตัดเศษสตางค์ทิ้ง)

การคำนวณใช้ Fraction ทั้งหมด จึงไม่มีความคลาดจาก float
"""

from fractions import Fraction
import math

THRESHOLD_SATANG = 50_000  # 500 บาท
DISCOUNT_BULK = Fraction(5, 100)
DISCOUNT_MEMBER = Fraction(10, 100)
VAT_RATE = Fraction(7, 100)


def cafe_bill(items, member):
    # 1) ยอดรวมก่อนลด (จำนวนเต็มสตางค์)
    subtotal = sum(int(it["price"]) * int(it["qty"]) for it in items)
    amount = Fraction(subtotal)

    # 2) ลด 5% เมื่อยอดรวมตั้งแต่ 500 บาทขึ้นไป
    if subtotal >= THRESHOLD_SATANG:
        amount *= 1 - DISCOUNT_BULK

    # 3) สมาชิกลดอีก 10% บนยอดที่เหลือ
    if member:
        amount *= 1 - DISCOUNT_MEMBER

    # 4) VAT 7% ขั้นสุดท้าย
    amount *= 1 + VAT_RATE

    # 5) ปัดลงเป็นจำนวนเต็มสตางค์ (ปัดเศษครั้งเดียว)
    return math.floor(amount)


if __name__ == "__main__":
    # ตัวอย่าง: กาแฟ 3 แก้ว ราคา 180 บาท (18,000 สตางค์) รวม 540 บาท สมาชิก
    sample = [{"price": 18000, "qty": 3}]
    print(cafe_bill(sample, True))
