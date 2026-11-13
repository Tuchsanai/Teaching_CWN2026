"""คิดค่าส่งเมล็ดกาแฟของ BaanKafe

หน่วยภายในเป็นสตางค์ทั้งหมด คำนวณด้วย Fraction ไม่ปัดระหว่างขั้น
และปัดครึ่งขึ้นครั้งเดียวตอนท้ายสุด
"""

import math
from fractions import Fraction

WEIGHT_MIN_G = 1
WEIGHT_MAX_G = 30000
DISTANCE_SURCHARGE_KM = 100      # เกิน 100 กม. (ไม่รวม 100)
EXPRESS_NUM, EXPRESS_DEN = 3, 2  # ส่งด่วน คูณ 1.5
FAR_NUM, FAR_DEN = 6, 5          # ระยะไกล คูณ 1.2


def _require_weight(value):
    if type(value) is not int:
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม")
    if not WEIGHT_MIN_G <= value <= WEIGHT_MAX_G:
        raise ValueError(f"weight_g ต้องอยู่ระหว่าง {WEIGHT_MIN_G} ถึง {WEIGHT_MAX_G} กรัม")
    return value


def _require_distance(value):
    if type(value) not in (int, float):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if not math.isfinite(value) or value < 0:
        raise ValueError("distance_km ต้องเป็นจำนวนจำกัดและไม่ติดลบ")
    return Fraction(value)


def _require_flag(value):
    if type(value) is not bool:
        raise ValueError("express ต้องเป็น True หรือ False")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม รับ Fraction ที่ไม่ติดลบ"""
    return int((x * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    weight_g = _require_weight(weight_g)
    distance = _require_distance(distance_km)
    express = _require_flag(express)

    # ฐานตามน้ำหนัก (หน่วย: สตางค์)
    if weight_g <= 1000:
        fee = Fraction(4000)                       # 40 บาท
    elif weight_g <= 5000:
        fee = Fraction(8000)                       # 80 บาท
    else:
        # 80 บาท + กิโลกรัมละ 15 บาท ตามสัดส่วนของกรัมที่เกิน 5,000
        # 15 บาท/1000 กรัม = 1.5 สตางค์ต่อกรัม
        fee = Fraction(8000) + Fraction(weight_g - 5000) * Fraction(3, 2)

    # ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if distance > DISTANCE_SURCHARGE_KM:
        fee *= Fraction(FAR_NUM, FAR_DEN)

    # ส่งด่วน คิดเพิ่ม 50% คูณต่อจากข้อก่อน
    if express:
        fee *= Fraction(EXPRESS_NUM, EXPRESS_DEN)

    return _half_up(fee)


if __name__ == "__main__":
    # ค่าที่คำนวณมือไว้ (สตางค์)
    cases = [
        ((1000, 0, False), 4000),    # 40 บาท ขอบล่างของขั้นแรก
        ((1001, 0, False), 8000),    # 80 บาท เริ่มขั้นที่สอง
        ((5000, 0, False), 8000),    # 80 บาท ขอบบนของขั้นที่สอง
        ((5001, 0, False), 8002),    # 8001.5 ปัดครึ่งขึ้น
        ((6000, 0, False), 9500),    # 80 + 15 = 95 บาท
        ((30000, 0, False), 45500),  # 80 + 250 = 455 บาท
        ((1000, 100, False), 4000),  # ระยะเท่ากับ 100 ไม่คิดเพิ่ม
        ((1000, 100.5, False), 4800),  # 40 * 1.2
        ((1000, 0, True), 6000),     # 40 * 1.5
        ((1000, 101, True), 7200),   # 40 * 1.2 * 1.5
        ((5001, 0, True), 12002),    # 8001.5 * 1.5 = 12002.25
    ]
    for args, expected in cases:
        got = shipping_fee(*args)
        status = "ok" if got == expected else "FAIL"
        print(f"{status}  shipping_fee{args} = {got} (คาด {expected})")
