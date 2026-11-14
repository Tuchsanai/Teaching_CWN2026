from fractions import Fraction

# หน่วย: สตางค์ทั้งเข้าและออก; 500 บาท = 50000 สตางค์
# ลำดับ: ยอดรวม -> (>=50000) x95/100 -> (member) x90/100 -> VAT x107/100 -> ปัดครึ่งขึ้นครั้งเดียว


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    if not isinstance(member, bool):
        raise ValueError("member must be bool")
    if not isinstance(items, (list, tuple)):
        raise ValueError("items must be a list")
    total = 0
    for it in items:
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise ValueError("invalid item")
        p, q = it["price"], it["qty"]
        if not _is_int(p) or p < 0:
            raise ValueError("invalid price")
        if not _is_int(q) or q < 1:
            raise ValueError("invalid qty")
        total += p * q
    amt = Fraction(total)
    if total >= 50000:
        amt *= Fraction(95, 100)
    if member:
        amt *= Fraction(90, 100)
    amt *= Fraction(107, 100)
    return (2 * amt.numerator + amt.denominator) // (2 * amt.denominator)
