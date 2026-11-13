from fractions import Fraction
from decimal import Decimal


def _exact(x):
    """แปลงเป็น Fraction แบบแม่นยำ (หลีกเลี่ยงปัญหา float)"""
    if isinstance(x, float):
        return Fraction(Decimal(repr(x)))
    return Fraction(x)


def shipping_fee(weight_g, distance_km, express=False):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (1 บาท = 100 สตางค์)"""
    if isinstance(weight_g, bool) or isinstance(distance_km, bool):
        raise TypeError("weight_g และ distance_km ต้องเป็นตัวเลข")
    w = _exact(weight_g)
    d = _exact(distance_km)
    if not 1 <= w <= 30000:
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1 ถึง 30,000 กรัม")
    if d < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    # ฐานค่าส่ง (สตางค์)
    if w <= 1000:
        fee = Fraction(4000)
    elif w <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 กรัม ตามสัดส่วน
        fee = Fraction(8000) + (w - 5000) * Fraction(1500, 1000)

    if d > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)

    # ปัดเศษครึ่งขึ้นเป็นสตางค์เต็ม
    return int(fee + Fraction(1, 2)) // 1
