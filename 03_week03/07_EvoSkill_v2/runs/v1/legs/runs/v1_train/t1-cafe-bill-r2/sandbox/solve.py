from fractions import Fraction


def need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def need_bool(v, name):
    if type(v) is not bool:
        raise ValueError(f"{name} ต้องเป็น True/False")
    return v


def cafe_bill(items, member):
    # สมมติฐาน: price >= 0 (สตางค์), qty >= 1; list ว่าง = ยอด 0
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    need_bool(member, "member")
    subtotal = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("item ไม่ถูกต้อง")
        subtotal += need_int(it["price"], "price", 0) * need_int(it["qty"], "qty", 1)

    x = Fraction(subtotal)
    if subtotal >= 50000:  # 500 บาท
        x *= Fraction(95, 100)
    if member:
        x *= Fraction(90, 100)
    x *= Fraction(107, 100)  # VAT ขั้นสุดท้าย
    # ปัดครึ่งขึ้นครั้งเดียวตอนจบ (เงินที่ลูกค้าจ่าย)
    return int((x * 2 + 1) // 2)
