from fractions import Fraction


def _require_int(value, name, low=None):
    if type(value) is not int:  # ปฏิเสธ bool, float, str, None
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int, x ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def cafe_bill(items, member):
    """คิดยอดที่ลูกค้าต้องจ่าย (สตางค์, จำนวนเต็ม)

    items:  list ของ dict {"price": ราคาต่อชิ้นเป็นสตางค์, "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก (ลดอีก 10%)

    กฎ:
      1. ยอดรวมก่อนลด (subtotal) >= 500 บาท (50,000 สตางค์) ลด 5%
      2. member = True ลดอีก 10% (คิดต่อจากยอดหลังข้อ 1)
      3. บวก VAT 7% เป็นขั้นสุดท้าย
      4. ปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียวตอนท้าย (เงินที่ลูกค้าจ่ายให้ร้าน)
    """
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True หรือ False")

    subtotal = 0
    for entry in items:
        if type(entry) is not dict:
            raise ValueError("แต่ละรายการใน items ต้องเป็น dict")
        price = _require_int(entry.get("price"), "price", low=0)
        qty = _require_int(entry.get("qty"), "qty", low=1)
        subtotal += price * qty

    # ตรวจ input ทั้งหมดก่อนคำนวณ (ทำแล้วด้านบน) จากนั้นคิดด้วย Fraction ไม่มี float
    total = Fraction(subtotal)

    if subtotal >= 50_000:  # ยอดรวมก่อนลดตั้งแต่ 500 บาท
        total *= Fraction(95, 100)

    if member:
        total *= Fraction(90, 100)

    total *= Fraction(107, 100)  # VAT 7% ขั้นสุดท้าย

    return _half_up(total)


if __name__ == "__main__":
    # ตัวอย่าง: 600 บาท เป็นสมาชิก -> 600 * 0.95 * 0.90 * 1.07 = 548.91 บาท
    print(cafe_bill([{"price": 60_000, "qty": 1}], True))
