from fractions import Fraction


def _need_int(v, lo, hi=None):
    if type(v) is not int or v < lo or (hi is not None and v > hi):
        raise ValueError("invalid input")


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นสตางค์ (int).
    ข้อสันนิษฐานจาก house-rules (โจทย์ไม่ได้ระบุ):
      - ส่งด่วนและน้ำหนัก > 20000 g -> ValueError
      - ระยะ 0 กม. (รับเองที่ร้าน) -> 0 (ตรวจ input/ข้อห้ามด่วนก่อน)
      - ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
    """
    _need_int(weight_g, 1, 30000)
    _need_int(distance_km, 0)
    if type(express) is not bool:
        raise ValueError("express must be bool")
    if express and weight_g > 20000:
        raise ValueError("express supports up to 20000 g")
    if distance_km == 0:
        return 0
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction(1500 * (weight_g - 5000), 1000)
    if distance_km > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return int((fee * 2 + 1) // 2)
