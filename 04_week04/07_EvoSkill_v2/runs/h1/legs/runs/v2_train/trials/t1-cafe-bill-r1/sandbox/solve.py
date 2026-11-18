from fractions import Fraction


def _require_int(value, name, low=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    return value


def _require_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int, x ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    items  : list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member : True ถ้าเป็นสมาชิก (ลดอีก 10%)

    ลำดับการคิด:
      1. ยอดรวม = sum(price * qty)
      2. ถ้ายอดรวม >= 50,000 สตางค์ (500 บาท) ลด 5%
      3. ถ้าเป็นสมาชิก ลดอีก 10% (คิดต่อจากยอดหลังขั้น 2)
      4. บวก VAT 7% เป็นขั้นสุดท้าย
      5. ปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียวตอนท้าย
    """
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")

    subtotal = 0
    for entry in items:
        if type(entry) is not dict:
            raise ValueError("แต่ละรายการใน items ต้องเป็น dict")
        price = _require_int(entry.get("price"), "price", low=0)
        qty = _require_int(entry.get("qty"), "qty", low=1)
        subtotal += price * qty

    member = _require_bool(member, "member")

    total = Fraction(subtotal)
    if subtotal >= 50_000:                       # 500 บาท = 50,000 สตางค์
        total *= Fraction(95, 100)               # ลด 5%
    if member:
        total *= Fraction(90, 100)               # ลดอีก 10%
    total *= Fraction(107, 100)                  # VAT 7% ขั้นสุดท้าย

    return _half_up(total)


if __name__ == "__main__":
    print(cafe_bill([{"price": 30000, "qty": 2}], False))   # 600 บาท -> 60000*0.95*1.07
    print(cafe_bill([{"price": 30000, "qty": 2}], True))
