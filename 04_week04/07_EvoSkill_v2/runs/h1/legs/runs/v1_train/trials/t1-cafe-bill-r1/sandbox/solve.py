from fractions import Fraction

THRESHOLD_SATANG = 50_000  # 500 บาท
THRESHOLD_DISCOUNT_PCT = 5
MEMBER_DISCOUNT_PCT = 10
VAT_PCT = 7


def _require_int(value, name, low=None):
    if type(value) is not int:  # ปฏิเสธ bool, float, str, None
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


def _percent_of(amount, pct):
    return Fraction(amount) * Fraction(pct, 100)


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่าย เป็นจำนวนเต็มสตางค์

    items: list ของ dict {"price": ราคาต่อชิ้น (สตางค์, int >= 0), "qty": จำนวนชิ้น (int >= 1)}
    member: bool, True = สมาชิกลดเพิ่ม 10%
    """
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    for entry in items:
        if type(entry) is not dict:
            raise ValueError("แต่ละรายการใน items ต้องเป็น dict")
        if "price" not in entry or "qty" not in entry:
            raise ValueError("แต่ละรายการต้องมี key 'price' และ 'qty'")
        _require_int(entry["price"], "price", low=0)
        _require_int(entry["qty"], "qty", low=1)
    _require_bool(member, "member")

    # 1) ยอดรวมก่อนลด (จำนวนเต็มล้วน ไม่มีการปัดเศษ)
    subtotal = sum(e["price"] * e["qty"] for e in items)

    # 2) ตัวคูณทั้งหมดคิดต่อกันโดยยังไม่ปัด
    total = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:  # เงื่อนไขตามยอดก่อนลด
        total -= _percent_of(total, THRESHOLD_DISCOUNT_PCT)
    if member:
        total -= _percent_of(total, MEMBER_DISCOUNT_PCT)  # คิดต่อจากยอดที่ลดแล้ว
    total += _percent_of(total, VAT_PCT)  # VAT ขั้นสุดท้าย

    # 3) ปัดครั้งเดียวตอนท้ายสุด ครึ่งขึ้น
    return _half_up(total)


if __name__ == "__main__":
    print(cafe_bill([{"price": 6000, "qty": 10}], True))
