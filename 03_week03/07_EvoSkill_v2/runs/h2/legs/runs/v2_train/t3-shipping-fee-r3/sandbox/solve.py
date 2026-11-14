"""BaanKafe: คิดค่าส่งเมล็ดกาแฟ

shipping_fee(weight_g, distance_km, express) -> int (จำนวนเต็มสตางค์)

ลำดับการคิด (ทุกขั้นเป็น Fraction ไม่ใช้ float):
  1. ค่าส่งตามน้ำหนัก (บาท)
       w <= 1,000 g           -> 40
       1,000 < w <= 5,000 g   -> 80
       w > 5,000 g            -> 80 + 15 * (w - 5,000) / 1,000   (คิดตามสัดส่วนกรัม)
  2. ระยะทาง > 100 กม.         -> คูณ 1.20 (เกิน 100 พอดีไม่คิด)
  3. ส่งด่วน (express=True)    -> คูณ 1.50 ต่อจากข้อ 2
  4. แปลงเป็นสตางค์ แล้วปัดลง (ตัดเศษสตางค์ทิ้ง) ที่ขั้นสุดท้ายครั้งเดียว
       ค่าเริ่มต้นเลือก "ปัดลง" เพราะโจทย์ไม่ได้ระบุโหมดปัด
"""

from fractions import Fraction
import math

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000

BASE_LIGHT = Fraction(40)           # ไม่เกิน 1,000 กรัม
BASE_MEDIUM = Fraction(80)          # 1,001 - 5,000 กรัม (และเป็นฐานของส่วนที่เกิน 5,000)
LIGHT_LIMIT_G = 1_000
MEDIUM_LIMIT_G = 5_000
PER_KG_OVER_LIMIT = Fraction(15)    # บาทต่อกิโลกรัม ส่วนที่เกิน 5,000 กรัม

LONG_DISTANCE_KM = Fraction(100)
LONG_DISTANCE_SURCHARGE = Fraction(120, 100)   # +20%
EXPRESS_SURCHARGE = Fraction(150, 100)         # +50%


def _to_fraction(value):
    """แปลง input เป็น Fraction โดยไม่ผ่าน float ของ binary (เช่น 0.1 -> 1/10)"""
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        return Fraction(repr(value))
    return Fraction(str(value))


def shipping_fee(weight_g, distance_km, express):
    weight = _to_fraction(weight_g)
    distance = _to_fraction(distance_km)

    if not (MIN_WEIGHT_G <= weight <= MAX_WEIGHT_G):
        raise ValueError(f"weight_g ต้องอยู่ในช่วง {MIN_WEIGHT_G}-{MAX_WEIGHT_G} กรัม")
    if distance < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    # 1) ค่าส่งตามน้ำหนัก (บาท)
    if weight <= LIGHT_LIMIT_G:
        fee = BASE_LIGHT
    elif weight <= MEDIUM_LIMIT_G:
        fee = BASE_MEDIUM
    else:
        fee = BASE_MEDIUM + PER_KG_OVER_LIMIT * (weight - MEDIUM_LIMIT_G) / 1000

    # 2) ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if distance > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_SURCHARGE

    # 3) ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
    if express:
        fee *= EXPRESS_SURCHARGE

    # 4) เป็นสตางค์ แล้วปัดลงครั้งเดียว
    return math.floor(fee * 100)


if __name__ == "__main__":
    print(shipping_fee(500, 10, False))     # 4000 (40 บาท)
    print(shipping_fee(7000, 120, True))    # 19800 (110 * 1.2 * 1.5 = 198 บาท)
