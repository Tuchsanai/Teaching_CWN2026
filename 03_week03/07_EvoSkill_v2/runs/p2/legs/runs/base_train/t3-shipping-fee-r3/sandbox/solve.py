from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (คำนวณแบบเศษส่วนแน่นอน ปัดครึ่งขึ้นตอนท้าย)"""
    if not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)  # 15 บาท/กก. = 1.5 สตางค์/กรัม

    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)

    return int((fee * 2 + 1) // 2)
