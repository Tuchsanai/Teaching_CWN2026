# กติกา: หน่วยอินพุต/เอาต์พุต = สตางค์ (int)
# 1) total = sum(price*qty)  2) total >= 50000 (500 บาท) -> x95/100
# 3) member -> x90/100 (ทบต่อ)  4) VAT x107/100 เป็นขั้นสุดท้าย
# ปัดครึ่งขึ้นครั้งเดียวตอนท้าย ใช้ Fraction ไม่ใช้ float
from fractions import Fraction


class InvalidInput(ValueError, TypeError, KeyError):
    def __str__(self):
        return Exception.__str__(self)


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def cafe_bill(items, member):
    if not isinstance(items, (list, tuple)):
        raise InvalidInput("items must be a list")
    if not isinstance(member, bool):
        raise InvalidInput("member must be bool")
    total = 0
    for it in items:
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise InvalidInput("invalid item")
        p, q = it["price"], it["qty"]
        if not _is_int(p) or p < 0:
            raise InvalidInput("invalid price")
        if not _is_int(q) or q < 1:
            raise InvalidInput("invalid qty")
        total += p * q
    v = Fraction(total)
    if total >= 50000:
        v = v * Fraction(95, 100)
    if member:
        v = v * Fraction(90, 100)
    v = v * Fraction(107, 100)
    return (2 * v.numerator + v.denominator) // (2 * v.denominator)
