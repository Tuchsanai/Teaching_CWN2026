from fractions import Fraction


class InputError(ValueError, TypeError):
    """input ผิด — เป็นทั้ง ValueError และ TypeError"""


def _check_int(name, v, lo):
    if isinstance(v, bool) or not isinstance(v, int):
        raise InputError(f"{name} must be an int, got {v!r}")
    if v < lo:
        raise InputError(f"{name} must be >= {lo}")
    return v


def cafe_bill(items, member):
    if not isinstance(member, bool):
        raise InputError(f"member must be a bool, got {member!r}")
    if not isinstance(items, (list, tuple)):
        raise InputError("items must be a list")
    subtotal = 0
    for it in items:
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise InputError("each item must be a dict with price and qty")
        subtotal += _check_int("price", it["price"], 0) * _check_int("qty", it["qty"], 1)

    # สมมติฐาน: เกณฑ์ 500 บาท (50000 สตางค์) ใช้กับยอดรวมก่อนลด (>=)
    total = Fraction(subtotal)
    if subtotal >= 50000:
        total *= Fraction(95, 100)
    if member:
        total *= Fraction(90, 100)
    total *= Fraction(107, 100)  # VAT ขั้นสุดท้าย
    # ปัดครึ่งขึ้นครั้งเดียวที่ยอดสุดท้าย
    return (2 * total.numerator + total.denominator) // (2 * total.denominator)
