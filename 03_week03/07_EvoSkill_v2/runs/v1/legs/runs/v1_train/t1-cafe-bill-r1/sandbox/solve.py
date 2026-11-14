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
    # ตรวจอินพุตก่อนคำนวณ (list ว่างถือว่าถูกต้อง ยอด 0)
    if type(items) is not list:
        raise ValueError("items ต้องเป็น list")
    need_bool(member, "member")
    total = 0
    for it in items:
        if type(it) is not dict:
            raise ValueError("แต่ละรายการต้องเป็น dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("รายการขาด key price/qty")
        price = need_int(it["price"], "price", low=0)  # สมมติ: ราคา >= 0
        qty = need_int(it["qty"], "qty", low=1)
        total += price * qty

    amount = Fraction(total)
    if total >= 50000:  # 500 บาท = 50000 สตางค์ เทียบยอดก่อนลด
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)  # VAT ขั้นสุดท้าย
    # ลูกค้าจ่าย: ปัดครึ่งขึ้นครั้งเดียวตอนจบ
    return int((amount * 2 + 1) // 2)
