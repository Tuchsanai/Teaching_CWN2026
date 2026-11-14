from fractions import Fraction


def cafe_bill(items, member):
    # หน่วยสตางค์; เกณฑ์ 500 บาท = 50000 สตางค์ (>= ตัดสินจากยอดก่อนลด)
    total = Fraction(sum(i["price"] * i["qty"] for i in items))
    if total >= 50000:
        total *= Fraction(95, 100)
    if member:
        total *= Fraction(90, 100)
    total *= Fraction(107, 100)
    # คำนวณแม่นยำ ปัดครึ่งไปหาเลขคู่ (banker's) ครั้งเดียวตอนท้าย
    return int(round(total))
