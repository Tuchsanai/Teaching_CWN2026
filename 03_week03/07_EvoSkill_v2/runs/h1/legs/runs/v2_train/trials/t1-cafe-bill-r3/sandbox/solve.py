"""BaanKafe: คิดเงินหน้าร้าน

กฎ (ตามลำดับ):
1. ยอดรวม = ผลรวม(price * qty) เป็นสตางค์ (จำนวนเต็ม)
2. ถ้ายอดรวมตั้งแต่ 500 บาท (50000 สตางค์) ขึ้นไป ลด 5%
3. ถ้าเป็นสมาชิก (member=True) ลดอีก 10% คิดต่อจากยอดที่ลดแล้ว
4. บวก VAT 7% เป็นขั้นสุดท้าย
5. ปัดครึ่งขึ้นครั้งเดียวตอนท้าย (ลูกค้าจ่ายให้ร้าน) คืนเป็นจำนวนเต็มสตางค์

ไม่ใช้ float ตลอดการคำนวณ ใช้ fractions.Fraction แทน
"""

from fractions import Fraction

THRESHOLD_SATANG = 500 * 100  # 500 บาท
DISCOUNT_BULK = Fraction(5, 100)
DISCOUNT_MEMBER = Fraction(10, 100)
VAT = Fraction(7, 100)


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
    """ปัดครึ่งขึ้นเป็น int สำหรับ x >= 0 (x เป็น Fraction)"""
    return int((x * 2 + 1) // 2)


def _validate_items(items):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    for entry in items:
        if type(entry) is not dict:
            raise ValueError("แต่ละรายการใน items ต้องเป็น dict")
        if "price" not in entry or "qty" not in entry:
            raise ValueError("แต่ละรายการต้องมี key 'price' และ 'qty'")
        _require_int(entry["price"], "price (สตางค์)", low=0)
        _require_int(entry["qty"], "qty", low=1)


def cafe_bill(items, member):
    """คืนยอดที่ลูกค้าต้องจ่ายเป็นจำนวนเต็มสตางค์"""
    _validate_items(items)
    _require_bool(member, "member")

    subtotal = sum(e["price"] * e["qty"] for e in items)  # จำนวนเต็มล้วน

    total = Fraction(subtotal)
    if subtotal >= THRESHOLD_SATANG:
        total -= total * DISCOUNT_BULK
    if member:
        total -= total * DISCOUNT_MEMBER
    total += total * VAT

    return _half_up(total)


if __name__ == "__main__":
    sample = [{"price": 15000, "qty": 2}, {"price": 6000, "qty": 1}]
    print(cafe_bill(sample, True))
