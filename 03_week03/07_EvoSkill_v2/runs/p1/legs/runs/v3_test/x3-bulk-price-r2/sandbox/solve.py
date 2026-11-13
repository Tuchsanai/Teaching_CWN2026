"""bulk_price — ราคาขายส่งเมล็ดกาแฟ BaanKafe (หน่วยสตางค์)

โหมดปัดเศษ: r2 = ปัดครึ่งไปหาเลขคู่ (banker's) ครั้งเดียวที่ยอดสุดท้าย
ข้อสมมติ:
- ส่วนลดปริมาณ (50+ → 7.5%, 10+ → 3.5%, ใช้อัตราเดียว) แล้วคูณส่วนลดคูปอง 2.5% ทบกัน
  แล้วคูณ VAT 7% เป็นขั้นสุดท้าย; ไม่ปัดกลางทาง
"""
from fractions import Fraction


class InputError(ValueError, TypeError):
    """input ผิด — เป็นทั้ง ValueError และ TypeError"""


def bulk_price(unit_price, qty, coupon):
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise InputError(f"unit_price must be an int, got {unit_price!r}")
    if unit_price < 0:
        raise InputError("unit_price must be >= 0")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise InputError(f"qty must be an int, got {qty!r}")
    if not 1 <= qty <= 1000:
        raise InputError("qty must be in 1..1000")
    if not isinstance(coupon, bool):
        raise InputError(f"coupon must be a bool, got {coupon!r}")

    total = Fraction(unit_price * qty)
    if qty >= 50:
        total *= Fraction(1000 - 75, 1000)
    elif qty >= 10:
        total *= Fraction(1000 - 35, 1000)
    if coupon:
        total *= Fraction(1000 - 25, 1000)
    total *= Fraction(107, 100)
    return int(round(total))
