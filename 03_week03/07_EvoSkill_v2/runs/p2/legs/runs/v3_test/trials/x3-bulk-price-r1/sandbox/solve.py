# หน่วย: สตางค์ (int) ทั้งอินพุต/เอาต์พุต
# ลำดับ: ยอดรวม = unit_price*qty -> ลดตามจำนวน (qty>=50: 7.5%, qty>=10: 3.5%, ใช้อัตราเดียว)
#        -> คูปองลด 2.5% -> VAT 7% (สุดท้าย)
# ปัดเศษ: นโยบายข้อ 1 (หลายขั้นต่อกัน) ปัด half-up เป็นสตางค์เต็มหลังทุกขั้น


class InvalidInput(ValueError, TypeError, KeyError):
    def __str__(self):
        return Exception.__str__(self)


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _half_up(num, den):
    return (2 * num + den) // (2 * den)


def bulk_price(unit_price, qty, coupon):
    if not _is_int(unit_price) or unit_price < 0:
        raise InvalidInput("unit_price must be int >= 0")
    if not _is_int(qty) or not (1 <= qty <= 1000):
        raise InvalidInput("qty must be int in 1..1000")
    if not isinstance(coupon, bool):
        raise InvalidInput("coupon must be bool")

    total = unit_price * qty
    if qty >= 50:
        total = _half_up(total * 925, 1000)
    elif qty >= 10:
        total = _half_up(total * 965, 1000)
    if coupon:
        total = _half_up(total * 975, 1000)
    total = _half_up(total * 107, 100)
    return int(total)
