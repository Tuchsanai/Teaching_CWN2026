from fractions import Fraction


def _need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def cafe_bill(items, member):
    # ตรวจอินพุตทั้งหมดก่อนคำนวณ
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    if type(member) is not bool:
        raise ValueError("member ต้องเป็น True/False")
    subtotal = 0
    for it in items:
        if type(it) is not dict:
            raise ValueError("item ต้องเป็น dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("item ต้องมี price และ qty")
        price = _need_int(it["price"], "price", 0)  # สมมติฐาน: ราคา 0 (ของแถม) ได้
        qty = _need_int(it["qty"], "qty", 1)
        subtotal += price * qty

    total = Fraction(subtotal)
    if subtotal >= 50000:  # 500 บาท = 50000 สตางค์ (เทียบยอดก่อนลด)
        total *= Fraction(95, 100)
    if member:
        total *= Fraction(90, 100)
    total *= Fraction(107, 100)  # VAT ขั้นสุดท้าย
    # ปัดครึ่งขึ้นครั้งเดียวตอนจบ (เงินที่ลูกค้าจ่าย)
    return int((total * 2 + 1) // 2)
