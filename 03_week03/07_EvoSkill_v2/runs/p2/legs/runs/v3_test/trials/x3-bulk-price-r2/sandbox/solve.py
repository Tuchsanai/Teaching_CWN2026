# bulk_price: หน่วยอินพุต/เอาต์พุต = สตางค์ (int)
# ลำดับ: ยอดรวม = unit_price*qty -> ลดตามจำนวน (>=50: 7.5%, >=10: 3.5%, ใช้อัตราเดียว)
#        -> คูปองลด 2.5% -> VAT 7% (ขั้นสุดท้าย)
# ปัดเศษ: นโยบายข้อ 1 (หลายขั้นตอนต่อกัน) ปัด half-up เป็นสตางค์เต็มหลังทุกขั้น
# ใช้จำนวนเต็มล้วน ไม่ใช้ float


class InvalidInput(ValueError, TypeError, KeyError):
    def __str__(self):
        return Exception.__str__(self)


def _half_up(num, den):
    return (2 * num + den) // (2 * den)


def bulk_price(unit_price, qty, coupon):
    if type(unit_price) is not int or unit_price < 0:
        raise InvalidInput("unit_price must be an int >= 0")
    if type(qty) is not int or not (1 <= qty <= 1000):
        raise InvalidInput("qty must be an int in 1..1000")
    if type(coupon) is not bool:
        raise InvalidInput("coupon must be a bool")

    total = unit_price * qty
    if qty >= 50:
        total = _half_up(total * 925, 1000)   # ลด 7.5%
    elif qty >= 10:
        total = _half_up(total * 965, 1000)   # ลด 3.5%
    if coupon:
        total = _half_up(total * 975, 1000)   # ลดอีก 2.5%
    total = _half_up(total * 107, 100)        # VAT 7%
    return int(total)
