from fractions import Fraction


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    # ตรวจอินพุตก่อนคำนวณ
    if not isinstance(member, bool):
        raise ValueError("member must be bool")
    if not isinstance(items, list):
        raise ValueError("items must be list")
    total = 0
    for it in items:
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise ValueError("invalid item")
        p, q = it["price"], it["qty"]
        if not _is_int(p) or not _is_int(q):
            raise ValueError("price/qty must be int")
        if p < 0 or q < 1:
            raise ValueError("price/qty out of range")
        total += p * q

    amt = Fraction(total)
    if total >= 50000:          # ตั้งแต่ 500 บาท (ยอดรวมก่อนลด)
        amt *= Fraction(95, 100)
    if member:
        amt *= Fraction(90, 100)
    amt *= Fraction(107, 100)   # VAT ขั้นสุดท้าย
    # ไม่ปัดกลางทาง ปัดลง (floor) ครั้งเดียวตอนจบ
    return amt.numerator // amt.denominator
