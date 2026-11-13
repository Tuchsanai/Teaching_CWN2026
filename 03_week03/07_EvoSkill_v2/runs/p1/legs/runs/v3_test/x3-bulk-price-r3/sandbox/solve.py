"""bulk_price — โหมด r3: ปัดครึ่งขึ้น (round half up) ทุกขั้นที่เป็นเงินสตางค์

ข้อสมมติ:
- ซื้อ >=50 ลด 7.5% (อัตราเดียว ไม่ซ้อนกับ 3.5%), >=10 ลด 3.5%
- เกณฑ์ใช้ qty ดิบ; ยอดรวม = unit_price*qty -> ลดตามปริมาณ (ปัด) -> คูปอง 2.5% (ปัด) -> VAT 7% (ปัด)
"""
from fractions import Fraction


class InputError(ValueError, TypeError):
    """input ผิด — เป็นทั้ง ValueError และ TypeError"""


def _round_half_up(x):
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def bulk_price(unit_price, qty, coupon):
    if isinstance(unit_price, bool) or not isinstance(unit_price, int):
        raise InputError(f"unit_price must be an int, got {unit_price!r}")
    if unit_price < 0:
        raise InputError("unit_price must be >= 0")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise InputError(f"qty must be an int, got {qty!r}")
    if qty < 1 or qty > 1000:
        raise InputError("qty must be in 1..1000")
    if not isinstance(coupon, bool):
        raise InputError(f"coupon must be a bool, got {coupon!r}")

    total = unit_price * qty
    if qty >= 50:
        total = _round_half_up(Fraction(total) * Fraction(925, 1000))
    elif qty >= 10:
        total = _round_half_up(Fraction(total) * Fraction(965, 1000))
    if coupon:
        total = _round_half_up(Fraction(total) * Fraction(975, 1000))
    total = _round_half_up(Fraction(total) * Fraction(107, 100))
    return int(total)
