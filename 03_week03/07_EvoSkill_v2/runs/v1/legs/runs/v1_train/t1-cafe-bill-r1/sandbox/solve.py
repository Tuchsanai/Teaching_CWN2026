from fractions import Fraction


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น bool")
    subtotal = 0
    for item in items:
        if type(item) is not dict or "price" not in item or "qty" not in item:
            raise ValueError("รายการไม่ถูกต้อง")
        subtotal += need_int(item["price"], "price", 0) * need_int(item["qty"], "qty", 1)
    amount = Fraction(subtotal)
    if subtotal >= 50000:
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    return half_up(amount * Fraction(107, 100))
