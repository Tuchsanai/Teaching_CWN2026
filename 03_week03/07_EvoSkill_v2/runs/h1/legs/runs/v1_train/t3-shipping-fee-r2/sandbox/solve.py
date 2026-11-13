"""ค่าส่งเมล็ดกาแฟ ร้าน BaanKafe

shipping_fee(weight_g, distance_km, express) -> int (หน่วยเป็นสตางค์)
"""

import math
from fractions import Fraction

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000
LONG_DISTANCE_KM = 100

# หน่วยสตางค์ (บาท x 100)
BASE_FEE_LIGHT = 40 * 100        # ไม่เกิน 1,000 กรัม
BASE_FEE_MEDIUM = 80 * 100       # ไม่เกิน 5,000 กรัม (และฐานของส่วนที่เกิน 5,000)
LIGHT_LIMIT_G = 1_000
MEDIUM_LIMIT_G = 5_000
# กิโลกรัมละ 15 บาท = 15 * 100 สตางค์ / 1000 กรัม ต่อ 1 กรัม (คิดตามสัดส่วน)
EXCESS_SATANG_PER_G = Fraction(15 * 100, 1000)


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม รับ int หรือ Fraction ที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def _require_int(value, label, lo, hi):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if value < lo or value > hi:
        raise ValueError(f"{label} ต้องอยู่ระหว่าง {lo} ถึง {hi}")
    return value


def _require_distance(value):
    if type(value) not in (int, float):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if not math.isfinite(value) or value < 0:
        raise ValueError("distance_km ต้องเป็นจำนวนจริงที่ไม่ติดลบ")
    return value


def _require_flag(value, label):
    if type(value) is not bool:
        raise ValueError(f"{label} ต้องเป็น True หรือ False")
    return value


def shipping_fee(weight_g, distance_km, express):
    """คิดค่าส่งเมล็ดกาแฟ คืนค่าเป็นจำนวนเต็มสตางค์

    ลำดับการคิด:
      1. ค่าส่งตามน้ำหนัก (ส่วนที่เกิน 5,000 กรัม คิดตามสัดส่วน)
      2. ระยะทางเกิน 100 กม. คูณ 1.2
      3. ส่งด่วน คูณ 1.5 (คูณต่อจากข้อ 2)
      4. ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
    """
    weight_g = _require_int(weight_g, "weight_g", MIN_WEIGHT_G, MAX_WEIGHT_G)
    distance_km = _require_distance(distance_km)
    express = _require_flag(express, "express")

    # 1. ค่าส่งตามน้ำหนัก (Fraction เพื่อไม่ให้คลาดเคลื่อน)
    if weight_g <= LIGHT_LIMIT_G:
        fee = Fraction(BASE_FEE_LIGHT)
    elif weight_g <= MEDIUM_LIMIT_G:
        fee = Fraction(BASE_FEE_MEDIUM)
    else:
        fee = BASE_FEE_MEDIUM + (weight_g - MEDIUM_LIMIT_G) * EXCESS_SATANG_PER_G

    # 2. ระยะทางเกิน 100 กม. เพิ่ม 20%
    if distance_km > LONG_DISTANCE_KM:
        fee *= Fraction(120, 100)

    # 3. ส่งด่วน เพิ่ม 50% (คูณต่อจากข้อก่อน)
    if express:
        fee *= Fraction(150, 100)

    # 4. ปัดครั้งเดียว
    return _half_up(fee)


if __name__ == "__main__":
    # ตัวอย่างตรวจผล (ค่าเป็นสตางค์)
    cases = [
        ((500, 10, False), 4000),
        ((1000, 0, False), 4000),
        ((1001, 0, False), 8000),
        ((5000, 0, False), 8000),
        ((5001, 0, False), 8002),      # 8001.5 -> ปัดขึ้น
        ((6000, 0, False), 9500),
        ((30000, 0, False), 45500),
        ((1000, 100, False), 4000),    # 100 กม. ไม่เกิน ไม่คิดเพิ่ม
        ((1000, 100.5, False), 4800),
        ((1000, 50, True), 6000),
        ((1000, 101, True), 7200),
        ((5001, 0, True), 12002),      # 12002.25 -> 12002
        ((5001, 101, True), 14403),    # 14402.7 -> 14403
    ]
    for args, expected in cases:
        got = shipping_fee(*args)
        status = "ok" if got == expected else "FAIL"
        print(f"{status}  shipping_fee{args} = {got} (คาด {expected})")
