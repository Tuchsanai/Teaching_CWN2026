"""ค่าส่งเมล็ดกาแฟ BaanKafe

คิดค่าส่งเป็นสตางค์ (จำนวนเต็ม) ด้วย Fraction เพื่อไม่ให้เกิดความคลาดเคลื่อนจากทศนิยม
"""

from fractions import Fraction
from math import floor

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000

# ราคาฐานเป็นสตางค์ (1 บาท = 100 สตางค์)
BASE_LIGHT_SATANG = 40 * 100      # ไม่เกิน 1,000 กรัม
BASE_MEDIUM_SATANG = 80 * 100     # ไม่เกิน 5,000 กรัม (และเป็นฐานของส่วนที่เกิน 5,000 กรัม)
LIGHT_LIMIT_G = 1_000
MEDIUM_LIMIT_G = 5_000

# ส่วนที่เกิน 5,000 กรัม: 15 บาทต่อกิโลกรัม = 1,500 สตางค์ / 1,000 กรัม = 3/2 สตางค์ต่อกรัม
EXTRA_SATANG_PER_G = Fraction(1500, 1000)

LONG_DISTANCE_KM = 100
LONG_DISTANCE_MULTIPLIER = Fraction(120, 100)   # เพิ่ม 20%
EXPRESS_MULTIPLIER = Fraction(150, 100)         # เพิ่ม 50%


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : น้ำหนักเป็นกรัม (1–30,000)
    distance_km : ระยะทางเป็นกิโลเมตร (>= 0)
    express     : True = ส่งด่วน (เพิ่ม 50%, คิดต่อจากการคำนวณก่อนหน้า)
    """
    if not (MIN_WEIGHT_G <= weight_g <= MAX_WEIGHT_G):
        raise ValueError(f"weight_g ต้องอยู่ระหว่าง {MIN_WEIGHT_G}–{MAX_WEIGHT_G} กรัม")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    w = Fraction(str(weight_g))
    d = Fraction(str(distance_km))

    # 1) ค่าส่งฐานตามน้ำหนัก
    if w <= LIGHT_LIMIT_G:
        fee = Fraction(BASE_LIGHT_SATANG)
    elif w <= MEDIUM_LIMIT_G:
        fee = Fraction(BASE_MEDIUM_SATANG)
    else:
        fee = BASE_MEDIUM_SATANG + EXTRA_SATANG_PER_G * (w - MEDIUM_LIMIT_G)

    # 2) ระยะทางเกิน 100 กม. เพิ่ม 20%
    if d > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_MULTIPLIER

    # 3) ส่งด่วนเพิ่ม 50% (คูณต่อจากข้อก่อน)
    if express:
        fee *= EXPRESS_MULTIPLIER

    # ปัดเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น)
    return floor(fee + Fraction(1, 2))
