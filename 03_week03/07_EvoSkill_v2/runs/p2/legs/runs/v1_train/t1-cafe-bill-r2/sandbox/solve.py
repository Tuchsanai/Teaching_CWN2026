# นโยบายปัดเศษ r2: ปัดครึ่งขึ้นเป็นสตางค์เต็มทุกขั้นที่ได้ยอดเงินใหม่


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _half_up(num, den):
    return (2 * num + den) // (2 * den)


def cafe_bill(items, member):
    if not isinstance(items, (list, tuple)) or len(items) == 0:
        raise ValueError("items must be a non-empty list")
    total = 0
    for it in items:
        try:
            price, qty = it["price"], it["qty"]
        except (KeyError, TypeError):
            raise ValueError("invalid item")
        if not _is_int(price) or not _is_int(qty) or price < 0 or qty < 1:
            raise ValueError("invalid price/qty")
        total += price * qty
    if total >= 50000:  # ตั้งแต่ 500 บาท (ก่อนหักส่วนลด)
        total = _half_up(total * 95, 100)
    if member:
        total = _half_up(total * 90, 100)
    return _half_up(total * 107, 100)
