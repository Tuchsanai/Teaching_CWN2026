# หน่วย: อินพุต/เอาต์พุตเป็นสตางค์ (int)
# ขั้นตอน: รวมยอด -> (>= 50000 สตางค์) ลด 5% -> member ลดอีก 10% (ทบกัน) -> VAT 7% ขั้นสุดท้าย
# ปัดครึ่งขึ้นครั้งเดียวตอนท้าย ใช้จำนวนเต็มล้วน


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
    num, den = total, 1
    if total >= 50000:
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100
    return int((2 * num + den) // (2 * den))
