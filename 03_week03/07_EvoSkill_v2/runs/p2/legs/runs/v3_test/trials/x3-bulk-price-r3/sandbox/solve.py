# กติกา: unit_price สตางค์ (int >= 0), qty 1-1000 (int), coupon bool -> คืนสตางค์ int
# ลำดับ: subtotal = unit*qty -> ลดตามปริมาณ (qty>=50: 7.5%, qty>=10: 3.5%, อัตราเดียว)
#        -> คูปองลดอีก 2.5% -> VAT 7% (ขั้นสุดท้าย)
# ปัดเศษ: นโยบายข้อ 1 - half-up เป็นสตางค์เต็มหลังทุกขั้น (ส่วนลดแต่ละตัว, VAT)


class InvalidInput(ValueError, TypeError, KeyError):
    def __str__(self):
        return Exception.__str__(self)


def _half_up(num, den):
    return (2 * num + den) // (2 * den)


def bulk_price(unit_price, qty, coupon):
    if type(unit_price) is not int or unit_price < 0:
        raise InvalidInput("unit_price must be int >= 0")
    if type(qty) is not int or not (1 <= qty <= 1000):
        raise InvalidInput("qty must be int in 1..1000")
    if type(coupon) is not bool:
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
