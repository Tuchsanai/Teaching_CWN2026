from fractions import Fraction
import math


def cafe_bill(items, member):
    total = sum(i["price"] * i["qty"] for i in items)
    a = Fraction(total)
    if total >= 50000:  # 500 บาท = 50000 สตางค์
        a *= Fraction(95, 100)
    if member:
        a *= Fraction(90, 100)
    a *= Fraction(107, 100)
    return int(math.ceil(a))  # ปัดขึ้นครั้งเดียวตอนจบ
