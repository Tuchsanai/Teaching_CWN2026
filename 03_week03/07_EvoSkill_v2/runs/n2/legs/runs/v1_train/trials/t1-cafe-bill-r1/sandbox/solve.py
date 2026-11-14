"""BaanKafe cafe_bill — คิดเงินหน้าร้าน (หน่วยสตางค์)"""
from fractions import Fraction


def _half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def _need_int(value, name, low):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if value < low:
        raise ValueError(f"{name} ต้องไม่ต่ำกว่า {low}")
    return value


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น bool")
    subtotal = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("item ไม่ถูกต้อง")
        subtotal += _need_int(it["price"], "price", 0) * _need_int(it["qty"], "qty", 1)
    amount = Fraction(subtotal)
    if subtotal >= 50000:  # ตั้งแต่ 500 บาท (เทียบกับยอดก่อนลด)
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)
    return _half_up(amount)  # ปัดครึ่งขึ้นครั้งเดียวตอนจบ
