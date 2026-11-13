from fractions import Fraction


def _half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True/False")
    total = 0
    for it in items:
        if type(it) is not dict:
            raise ValueError("item ต้องเป็น dict")
        price = it.get("price")
        qty = it.get("qty")
        if type(price) is not int or price < 0:
            raise ValueError("price ไม่ถูกต้อง")
        if type(qty) is not int or qty < 1:
            raise ValueError("qty ไม่ถูกต้อง")
        total += price * qty
    amt = Fraction(total)
    if total >= 50000:
        amt *= Fraction(95, 100)
    if member:
        amt *= Fraction(90, 100)
    amt *= Fraction(107, 100)
    return _half_up(amt)
