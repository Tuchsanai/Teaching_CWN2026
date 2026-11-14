"""BaanKafe cafe_bill — หน่วยสตางค์, ใช้ Fraction, ปัด half-up ครั้งเดียวท้ายสุด"""
from fractions import Fraction


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def _need_int(value, name, low=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True หรือ False")
    subtotal = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("item ต้องเป็น dict ที่มี price และ qty")
        subtotal += _need_int(it["price"], "price", 0) * _need_int(it["qty"], "qty", 1)
    x = Fraction(subtotal)
    if subtotal >= 50000:
        x *= Fraction(95, 100)
    if member:
        x *= Fraction(90, 100)
    x *= Fraction(107, 100)
    return half_up(x)
