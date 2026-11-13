from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น) คำนวณด้วย Fraction เพื่อเลี่ยงความคลาดเคลื่อนของ float"""
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 กรัม ตามสัดส่วน
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)

    if Fraction(distance_km) > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)

    return int((fee + Fraction(1, 2)) // 1)
