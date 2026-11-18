# กติกา: หน่วยเอาต์พุต = สตางค์ (int); 1 บาท = 100 สตางค์
# <=1000g 4000 | <=5000g 8000 | >5000g 8000 + ส่วนเกิน*1.5 สตางค์/กรัม (15 บาท/กก.)
# ระยะทาง > 100 กม. x1.2 ; express x1.5 (ทบต่อกัน) ; ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
import math
from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    if isinstance(weight_g, bool) or not isinstance(weight_g, int):
        raise ValueError("weight_g must be an int")
    if not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be 1-30000")
    if isinstance(distance_km, bool) or not isinstance(distance_km, (int, float)):
        raise ValueError("distance_km must be a number")
    if isinstance(distance_km, float) and not math.isfinite(distance_km):
        raise ValueError("distance_km must be finite")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")
    if not isinstance(express, bool):
        raise ValueError("express must be a bool")

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction(3 * (weight_g - 5000), 2)
    if distance_km > 100:
        fee *= Fraction(12, 10)
    if express:
        fee *= Fraction(3, 2)
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)
