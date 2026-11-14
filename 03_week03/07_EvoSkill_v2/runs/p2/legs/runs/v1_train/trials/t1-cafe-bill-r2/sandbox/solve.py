# กติกา: price/ผลลัพธ์เป็นสตางค์ (500 บาท = 50000 สตางค์)
# ลำดับ: รวมยอด -> (>= 50000) ลด 5% -> member ลดอีก 10% (ทบกัน) -> VAT 7% ขั้นสุดท้าย
# ปัดครึ่งขึ้นครั้งเดียวตอนท้าย ใช้จำนวนเต็มล้วน
def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    if not isinstance(items, (list, tuple)):
        raise ValueError("items must be a list")
    if not isinstance(member, bool):
        raise ValueError("member must be bool")
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
