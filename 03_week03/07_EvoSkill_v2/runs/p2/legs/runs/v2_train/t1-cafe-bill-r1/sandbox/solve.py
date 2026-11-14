from fractions import Fraction


def cafe_bill(items, member):
    # แบบ H: Fraction ตลอด ปัดครึ่งขึ้นครั้งเดียวตอนท้าย ตรวจอินพุตนอกช่วง
    total = 0
    for it in items:
        price, qty = it["price"], it["qty"]
        if price < 0 or qty < 1:
            raise ValueError("invalid item")
        total += price * qty
    x = Fraction(total)
    if total >= 50000:  # 500 บาท ตัดสินจากยอดก่อนลด
        x *= Fraction(95, 100)
    if member:
        x *= Fraction(90, 100)
    x *= Fraction(107, 100)  # VAT ขั้นสุดท้าย
    n, d = x.numerator, x.denominator
    return int((2 * n + d) // (2 * d))
