from fractions import Fraction


def _half_up(x):
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
        p, q = it["price"], it["qty"]
        if type(p) is not int or p < 0:
            raise ValueError("price ต้องเป็นจำนวนเต็มตั้งแต่ 0")
        if type(q) is not int or q < 1:
            raise ValueError("qty ต้องเป็นจำนวนเต็มตั้งแต่ 1")
        total += p * q
    x = Fraction(total)
    if total >= 50000:
        x *= Fraction(95, 100)
    if member:
        x *= Fraction(90, 100)
    x *= Fraction(107, 100)
    return _half_up(x)
