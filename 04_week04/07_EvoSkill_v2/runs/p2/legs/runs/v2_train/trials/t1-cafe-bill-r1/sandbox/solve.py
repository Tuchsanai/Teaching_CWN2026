# หน่วย: อินพุต/เอาต์พุตเป็นสตางค์ (int); 500 บาท = 50000 สตางค์
# ลำดับ: รวมยอด -> (>=50000) ลด 5% -> member ลด 10% -> VAT 7% (สุดท้าย) -> ปัดครึ่งขึ้นครั้งเดียว


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
            raise InvalidInput("price must be int >= 0")
        if not _is_int(q) or q < 1:
            raise InvalidInput("qty must be int >= 1")
        total += p * q
    num, den = total, 1
    if total >= 50000:
        num *= 95
        den *= 100
    if member:
        num *= 90
        den *= 100
    num *= 107
    den *= 100
    return (2 * num + den) // (2 * den)
