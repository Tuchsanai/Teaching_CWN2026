from fractions import Fraction
import math


def cafe_bill(items, member):
    """คิดเงินหน้าร้าน BaanKafe

    items  : list ของ {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member : True ถ้าเป็นสมาชิก

    ลำดับการคิด (ทำงานในหน่วยสตางค์ ไม่ปัดระหว่างทาง):
      1. ยอดรวม (subtotal) = sum(price * qty)
      2. ถ้ายอดรวม >= 500 บาท (50,000 สตางค์) ลด 5% บนยอดรวม
      3. ถ้าเป็นสมาชิก ลดอีก 10% บนยอดที่เหลือจากข้อ 2 (ลดต่อเนื่อง)
      4. บวก VAT 7% เป็นขั้นสุดท้ายบนยอดหลังส่วนลดทั้งหมด
      5. ปัดลง (ตัดเศษสตางค์ทิ้ง) ครั้งเดียวที่ขั้นสุดท้าย

    คืนค่า: จำนวนเต็มสตางค์ที่ลูกค้าต้องจ่าย
    """
    subtotal = sum(Fraction(item["price"]) * item["qty"] for item in items)

    total = subtotal
    if subtotal >= 50000:  # 500 บาท = 50,000 สตางค์
        total *= Fraction(95, 100)  # ลด 5%

    if member:
        total *= Fraction(90, 100)  # ลดอีก 10% (ต่อเนื่องจากข้อก่อน)

    total *= Fraction(107, 100)  # VAT 7% ขั้นสุดท้าย

    return math.floor(total)  # ปัดลง (ค่าเริ่มต้น เพราะโจทย์ไม่ระบุการปัด)


if __name__ == "__main__":
    # ตัวอย่าง: กาแฟ 3 แก้ว แก้วละ 250 บาท (25,000 สตางค์) รวม 750 บาท, เป็นสมาชิก
    sample = [{"price": 25000, "qty": 3}]
    print(cafe_bill(sample, True))
