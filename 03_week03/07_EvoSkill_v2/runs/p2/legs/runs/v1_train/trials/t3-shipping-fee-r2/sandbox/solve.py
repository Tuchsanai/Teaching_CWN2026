# กติกา: อินพุต weight_g (กรัม int 1-30000), distance_km (>=0), express (bool)
# ค่าส่ง (บาท): <=1000g 40 | <=5000g 80 | >5000g 80 + (w-5000)/1000*15
# ระยะทาง > 100 กม. x1.2 ; ด่วน x1.5 (ทบต่อ) ; ผลลัพธ์เป็นสตางค์ ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
from fractions import Fraction
import math


def shipping_fee(weight_g, distance_km, express):
    if isinstance(weight_g, bool) or not isinstance(weight_g, int):
        raise ValueError("weight_g must be an int")
    if not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be between 1 and 30000")
    if isinstance(distance_km, bool) or not isinstance(distance_km, (int, float)):
        raise ValueError("distance_km must be a number")
    if isinstance(distance_km, float) and not math.isfinite(distance_km):
        raise ValueError("distance_km must be finite")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")
    if not isinstance(express, bool):
        raise ValueError("express must be a bool")

    if weight_g <= 1000:
        baht = Fraction(40)
    elif weight_g <= 5000:
        baht = Fraction(80)
    else:
        baht = 80 + Fraction(weight_g - 5000, 1000) * 15
    if distance_km > 100:
        baht *= Fraction(12, 10)
    if express:
        baht *= Fraction(3, 2)
    satang = baht * 100
    return (2 * satang.numerator + satang.denominator) // (2 * satang.denominator)
