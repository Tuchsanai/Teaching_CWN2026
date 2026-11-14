from fractions import Fraction


def _half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    # ตรวจ input
    if type(weight_g) is not int or not (1 <= weight_g <= 30000):
        raise ValueError("weight_g must be int 1-30000")
    if type(distance_km) is not int or distance_km < 0:
        raise ValueError("distance_km must be int >= 0")
    if type(express) is not bool:
        raise ValueError("express must be bool")
    # ข้อสันนิษฐานตาม house-rules (โจทย์ไม่ได้ระบุ):
    # ส่งด่วนรับไม่เกิน 20,000 กรัม
    if express and weight_g > 20000:
        raise ValueError("express supports at most 20000 g")
    # ระยะ 0 กม. = รับเองที่ร้าน ฟรี
    if distance_km == 0:
        return 0
    # หน่วยสตางค์
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = 8000 + Fraction(1500 * (weight_g - 5000), 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return _half_up(fee)
