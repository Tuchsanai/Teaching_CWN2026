from fractions import Fraction

# นโยบายปัดเศษ r1: คำนวณแม่นยำด้วย Fraction แล้วปัดครึ่งขึ้น (half-up) ครั้งเดียวตอนท้าย


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    if not isinstance(items, (list, tuple)) or len(items) == 0:
        raise ValueError("items must be a non-empty list")
    if not isinstance(member, bool):
        raise ValueError("member must be bool")
    total = 0
    for it in items:
        try:
            price, qty = it["price"], it["qty"]
        except (KeyError, TypeError):
            raise ValueError("each item needs price and qty")
        if not _is_int(price) or price < 0:
            raise ValueError("price must be int >= 0")
        if not _is_int(qty) or qty < 1:
            raise ValueError("qty must be int >= 1")
        total += price * qty

    amount = Fraction(total)
    if total >= 50000:  # ตั้งแต่ 500 บาท (ตัดสินจากยอดรวมก่อนลด)
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)  # VAT ขั้นสุดท้าย
    return int((amount * 2 + 1) // 2)  # half-up
