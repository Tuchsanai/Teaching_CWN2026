from fractions import Fraction

THRESHOLD_SATANG = 50_000            # 500 บาท (หน่วยสตางค์)
BULK_DISCOUNT = Fraction(5, 100)     # ลด 5% เมื่อยอดตั้งแต่ 500 บาท
MEMBER_DISCOUNT = Fraction(10, 100)  # ลดอีก 10% สำหรับสมาชิก
VAT = Fraction(7, 100)               # VAT 7% ขั้นสุดท้าย


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
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    items: list ของ {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก
    """
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True หรือ False")

    # ตรวจ input ทั้งหมดก่อนคำนวณ
    subtotal = 0
    for entry in items:
        if type(entry) is not dict:
            raise ValueError("แต่ละรายการใน items ต้องเป็น dict")
        price = _require_int(entry.get("price"), "price", low=0)
        qty = _require_int(entry.get("qty"), "qty", low=1)
        subtotal += price * qty

    # คำนวณเป็น Fraction ทั้งหมด ปัดเศษครั้งเดียวตอนท้าย
    total = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:       # เทียบกับยอดก่อนลด
        total -= total * BULK_DISCOUNT
    if member:
        total -= total * MEMBER_DISCOUNT   # คิดต่อจากยอดที่ลดแล้ว
    total += total * VAT                   # VAT เป็นขั้นสุดท้าย
    return _half_up(total)
