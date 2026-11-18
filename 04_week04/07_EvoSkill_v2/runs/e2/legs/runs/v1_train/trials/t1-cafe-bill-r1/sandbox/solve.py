"""BaanKafe cafe_bill: คิดเงินหน้าร้าน (หน่วยสตางค์)"""
from fractions import Fraction


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น bool")
    total = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("item ไม่ถูกต้อง")
        p, q = it["price"], it["qty"]
        if type(p) is not int or p < 0:
            raise ValueError("price ไม่ถูกต้อง")
        if type(q) is not int or q < 1:
            raise ValueError("qty ไม่ถูกต้อง")
        total += p * q
    x = Fraction(total)
    if total >= 50000:
        x *= Fraction(95, 100)
    if member:
        x *= Fraction(90, 100)
    x *= Fraction(107, 100)
    return half_up(x)
