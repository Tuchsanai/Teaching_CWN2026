from fractions import Fraction


def _need_int(v, name, low=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and v < low:
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


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
        price = _need_int(it.get("price"), "price", 0)
        qty = _need_int(it.get("qty"), "qty", 1)
        total += price * qty
    amt = Fraction(total)
    if total >= 50000:
        amt *= Fraction(95, 100)
    if member:
        amt *= Fraction(90, 100)
    amt *= Fraction(107, 100)
    return _half_up(amt)
