"""คำนวณค่าส่งเมล็ดกาแฟของร้าน BaanKafe

หน่วยภายในทั้งหมดเป็นสตางค์ (int) และใช้ Fraction ตลอดการคำนวณ
ปัดเศษครั้งเดียวตอนท้ายแบบครึ่งขึ้น (half-up)
"""

import math
from fractions import Fraction

# ค่าส่งฐาน (สตางค์)
BASE_UP_TO_1KG = 4000       # ไม่เกิน 1,000 กรัม = 40 บาท
BASE_UP_TO_5KG = 8000       # ไม่เกิน 5,000 กรัม = 80 บาท
# ส่วนที่เกิน 5,000 กรัม: 15 บาท/กก. = 1500 สตางค์ / 1000 กรัม
OVER_5KG_PER_GRAM = Fraction(1500, 1000)

MAX_WEIGHT_G = 30000
DISTANCE_SURCHARGE_LIMIT_KM = 100
DISTANCE_SURCHARGE = Fraction(6, 5)   # +20%
EXPRESS_MULTIPLIER = Fraction(3, 2)   # +50%


def _check_weight(weight_g):
    if type(weight_g) is not int:
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม")
    if not 1 <= weight_g <= MAX_WEIGHT_G:
        raise ValueError(f"weight_g ต้องอยู่ระหว่าง 1 ถึง {MAX_WEIGHT_G}")


def _check_distance(distance_km):
    if type(distance_km) not in (int, float):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if isinstance(distance_km, float) and not math.isfinite(distance_km):
        raise ValueError("distance_km ต้องเป็นจำนวนจำกัด")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่น้อยกว่า 0")


def _check_express(express):
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น True หรือ False")


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int, x ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    _check_weight(weight_g)
    _check_distance(distance_km)
    _check_express(express)

    if weight_g <= 1000:
        fee = Fraction(BASE_UP_TO_1KG)
    elif weight_g <= 5000:
        fee = Fraction(BASE_UP_TO_5KG)
    else:
        fee = Fraction(BASE_UP_TO_5KG) + (weight_g - 5000) * OVER_5KG_PER_GRAM

    if distance_km > DISTANCE_SURCHARGE_LIMIT_KM:
        fee *= DISTANCE_SURCHARGE

    if express:
        fee *= EXPRESS_MULTIPLIER

    return _half_up(fee)
