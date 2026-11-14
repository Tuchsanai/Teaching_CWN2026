from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (คำนวณแบบเศษส่วนตรง ปัดครึ่งขึ้นตอนท้ายสุดครั้งเดียว)"""
    if weight_g < 1 or weight_g > 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 กรัม ตามสัดส่วนกรัม
        fee = Fraction(8000) + (w - 5000) * 1500 / 1000

    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)

    return int((fee * 2 + 1) // 2)  # ปัดครึ่งขึ้น
