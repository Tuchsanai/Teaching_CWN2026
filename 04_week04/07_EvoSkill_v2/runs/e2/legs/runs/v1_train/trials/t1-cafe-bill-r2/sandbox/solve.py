"""BaanKafe: คิดเงินหน้าร้าน (หน่วยสตางค์)"""
from fractions import Fraction


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True หรือ False")
    total = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("แต่ละรายการต้องเป็น dict ที่มี price และ qty")
        price, qty = it["price"], it["qty"]
        if type(price) is not int or price < 0:
            raise ValueError("price ต้องเป็นจำนวนเต็ม >= 0")
        if type(qty) is not int or qty < 1:
            raise ValueError("qty ต้องเป็นจำนวนเต็ม >= 1")
        total += price * qty
    x = Fraction(total)
    if total >= 50000:
        x *= Fraction(95, 100)
    if member:
        x *= Fraction(90, 100)
    x *= Fraction(107, 100)
    return half_up(x)
