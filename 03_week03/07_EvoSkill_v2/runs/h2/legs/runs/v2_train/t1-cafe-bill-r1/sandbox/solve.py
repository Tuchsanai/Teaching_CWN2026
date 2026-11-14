from fractions import Fraction
import math


def cafe_bill(items, member):
    """คิดเงินหน้าร้าน BaanKafe

    items  : list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น}
    member : True ถ้าเป็นสมาชิก
    คืนค่า : ยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์

    ลำดับการคิด:
      1) ยอดรวมก่อนลด = sum(price * qty)
      2) ถ้ายอดรวม >= 50,000 สตางค์ (500 บาท) ลด 5%
      3) ถ้าเป็นสมาชิก ลดอีก 10% (คิดต่อจากยอดหลังข้อ 2)
      4) บวก VAT 7% เป็นขั้นสุดท้าย
      5) ปัดลง (ตัดเศษสตางค์ทิ้ง) ครั้งเดียวที่ขั้นสุดท้าย
    """
    # 1) ยอดรวมก่อนลด (หน่วยสตางค์ ไม่ใช้ float)
    subtotal = sum(item["price"] * item["qty"] for item in items)

    amount = Fraction(subtotal)

    # 2) ลด 5% เมื่อยอดรวมตั้งแต่ 500 บาทขึ้นไป
    if subtotal >= 50000:
        amount *= Fraction(95, 100)

    # 3) สมาชิกลดอีก 10% (ต่อเนื่องจากข้อ 2)
    if member:
        amount *= Fraction(90, 100)

    # 4) VAT 7% ขั้นสุดท้าย
    amount *= Fraction(107, 100)

    # 5) ปัดลงเป็นจำนวนเต็มสตางค์ครั้งเดียว
    return math.floor(amount)


if __name__ == "__main__":
    sample = [{"price": 15000, "qty": 4}]  # 600 บาท
    print(cafe_bill(sample, False))  # 600*0.95*1.07 = 609.90 บาท -> 60990
    print(cafe_bill(sample, True))   # 600*0.95*0.90*1.07 = 548.91 บาท -> 54891
