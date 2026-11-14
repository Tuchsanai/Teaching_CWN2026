# หน่วย: weight_g กรัม (int 1-30000), distance_km >= 0, express bool -> คืนสตางค์ (int)
# ค่าส่งฐาน (บาท): <=1000g 40 | <=5000g 80 | เกิน 80 + (w-5000)/1000*15
# >100 กม. x1.2 ; express x1.5 (ทบต่อ) ; ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
from fractions import Fraction


def shipping_fee(weight_g, distance_km, express):
    if isinstance(weight_g, bool) or not isinstance(weight_g, int):
        raise ValueError("weight_g must be int")
    if not 1 <= weight_g <= 30000:
        raise ValueError("weight_g out of range")
    if isinstance(distance_km, bool) or not isinstance(distance_km, (int, float)):
        raise ValueError("distance_km must be a number")
    if distance_km != distance_km or distance_km < 0 or distance_km == float("inf"):
        raise ValueError("distance_km invalid")
    if not isinstance(express, bool):
        raise ValueError("express must be bool")

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction((weight_g - 5000) * 1500, 1000)
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return (2 * fee.numerator + fee.denominator) // (2 * fee.denominator)
