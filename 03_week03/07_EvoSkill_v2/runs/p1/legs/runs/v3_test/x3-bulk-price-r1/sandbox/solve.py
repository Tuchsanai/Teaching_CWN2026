"""bulk_price — โหมดปัดเศษ r1: ปัดครึ่งขึ้นครั้งเดียวที่ยอดสุดท้าย

ข้อสมมติ:
- qty>=50 ลด 7.5%, qty>=10 ลด 3.5% (อัตราเดียว ไม่ซ้อนกัน)
- คูปองลดอีก 2.5% คูณทบต่อจากส่วนลดปริมาณ
- VAT 7% เป็นขั้นสุดท้าย; คำนวณด้วย Fraction ไม่ปัดกลางทาง
"""
from fractions import Fraction


class InputError(ValueError, TypeError):
    """input ผิด — เป็นทั้ง ValueError และ TypeError"""


def _check_int(name, v, lo, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise InputError(f"{name} must be an int, got {v!r}")
    if v < lo or (hi is not None and v > hi):
        raise InputError(f"{name} out of range: {v!r}")


def bulk_price(unit_price, qty, coupon):
    _check_int("unit_price", unit_price, 0)
    _check_int("qty", qty, 1, 1000)
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
    return (2 * total.numerator + total.denominator) // (2 * total.denominator)
