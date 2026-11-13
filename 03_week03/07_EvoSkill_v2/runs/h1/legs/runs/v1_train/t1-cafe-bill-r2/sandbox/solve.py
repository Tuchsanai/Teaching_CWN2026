from fractions import Fraction

# เกณฑ์และอัตราต่าง ๆ เก็บเป็นสตางค์ / เศษส่วนที่แน่นอน
THRESHOLD_SATANG = 50000          # 500 บาท (ตั้งแต่ 500 ขึ้นไป รวมค่า 500 บาทพอดี)
BULK_DISCOUNT = Fraction(95, 100)  # ลด 5%
MEMBER_DISCOUNT = Fraction(90, 100)  # ลดอีก 10% (คูณต่อจากส่วนลดก่อนหน้า)
VAT = Fraction(107, 100)           # บวก VAT 7% เป็นขั้นสุดท้าย


def _require_int(value, label, lo=None):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม รับ int หรือ Fraction ที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์), "qty": จำนวนชิ้น (>= 1)}
    member: True ถ้าเป็นสมาชิก
    """
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True หรือ False")

    subtotal = 0
    for i, item in enumerate(items):
        label = f"items[{i}]"
        if type(item) is not dict:
            raise ValueError(f"{label} ต้องเป็น dict")
        if "price" not in item or "qty" not in item:
            raise ValueError(f"{label} ต้องมี field price และ qty")
        price = _require_int(item["price"], f"{label}.price", lo=0)
        qty = _require_int(item["qty"], f"{label}.qty", lo=1)
        subtotal += price * qty

    # ขั้นที่ 1: ส่วนลดตามยอดรวม (เทียบก่อนหักส่วนลดสมาชิก)
    amount = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:
        amount *= BULK_DISCOUNT

    # ขั้นที่ 2: ส่วนลดสมาชิก คูณต่อจากขั้นที่ 1
    if member:
        amount *= MEMBER_DISCOUNT

    # ขั้นที่ 3: VAT เป็นขั้นสุดท้าย
    amount *= VAT

    # ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
    return _half_up(amount)


if __name__ == "__main__":
    print(cafe_bill([{"price": 10000, "qty": 1}], False))   # 10700
    print(cafe_bill([{"price": 50000, "qty": 1}], False))   # 50825
    print(cafe_bill([{"price": 50000, "qty": 1}], True))    # 45743
