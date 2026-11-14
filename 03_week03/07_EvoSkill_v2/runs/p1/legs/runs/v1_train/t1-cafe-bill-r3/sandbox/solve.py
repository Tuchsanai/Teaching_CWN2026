from fractions import Fraction


def _rnd(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (ใช้หลังทุกขั้นที่คูณเปอร์เซ็นต์)"""
    x = Fraction(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def cafe_bill(items, member):
    # ตรวจอินพุต: qty ต้องตั้งแต่ 1
    for it in items:
        if it["qty"] < 1:
            raise ValueError("qty must be >= 1")
    total = sum(it["price"] * it["qty"] for it in items)  # ยอดรวมก่อนลด
    if total >= 50000:  # 500 บาท = 50000 สตางค์ (ตั้งแต่ = >=)
        total = _rnd(Fraction(total * 95, 100))
    if member:
        total = _rnd(Fraction(total * 90, 100))
    total = _rnd(Fraction(total * 107, 100))  # VAT ขั้นสุดท้าย
    return int(total)
