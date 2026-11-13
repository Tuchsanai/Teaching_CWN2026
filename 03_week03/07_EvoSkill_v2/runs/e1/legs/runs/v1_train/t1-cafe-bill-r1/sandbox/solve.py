from fractions import Fraction


def _need_int(v, name, low=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and v < low:
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น bool")
    total = 0
    for it in items:
        if type(it) is not dict:
            raise ValueError("item ต้องเป็น dict")
        price = _need_int(it.get("price"), "price", 0)
        qty = _need_int(it.get("qty"), "qty", 1)
        total += price * qty
    x = Fraction(total)
    if total >= 50000:
        x *= Fraction(95, 100)
    if member:
        x *= Fraction(90, 100)
    x *= Fraction(107, 100)
    return int((x * 2 + 1) // 2)
