from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    # แบบ E: Fraction แม่นยำตลอด ปัดครึ่งไปหาเลขคู่ครั้งเดียวตอนท้าย ไม่ตรวจอินพุต
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)          # 40 บาท
    elif w <= 5000:
        fee = Fraction(8000)          # 80 บาท
    else:
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)  # 15 บาท/กก.
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return int(round(fee))
