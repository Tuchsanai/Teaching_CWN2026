from fractions import Fraction


def cafe_bill(items, member):
    """คืนยอดที่ต้องจ่ายเป็นจำนวนเต็มสตางค์ (คำนวณแบบแม่นยำ ปัดครั้งเดียวตอนท้าย)"""
    total = sum(i["price"] * i["qty"] for i in items)
    amount = Fraction(total)
    if total >= 50000:  # 500 บาท = 50000 สตางค์
        amount *= Fraction(95, 100)
    if member:
        amount *= Fraction(90, 100)
    amount *= Fraction(107, 100)
    return (amount.numerator * 2 + amount.denominator) // (amount.denominator * 2)  # ปัดครึ่งขึ้น
