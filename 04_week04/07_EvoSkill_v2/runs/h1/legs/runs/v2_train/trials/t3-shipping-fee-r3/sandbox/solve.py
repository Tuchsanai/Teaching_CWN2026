"""คิดค่าส่งเมล็ดกาแฟของ BaanKafe

หน่วยภายในเป็นสตางค์ทั้งหมด ผลลัพธ์เป็น int สตางค์
คำนวณด้วย Fraction และปัดครึ่งขึ้นครั้งเดียวตอนท้าย (ลูกค้าเป็นผู้จ่ายให้ร้าน)
"""

import math
from fractions import Fraction


def _require_int(value, name, low, high):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if value < low or value > high:
        raise ValueError(f"{name} ต้องอยู่ระหว่าง {low} ถึง {high}")
    return value


def _require_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def _require_non_negative_number(value, name):
    if type(value) not in (int, float):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} ต้องเป็นตัวเลขจำกัดและไม่ติดลบ")
    return Fraction(value)


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int, x ไม่ติดลบ"""
    return int((x * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : int 1–30000 (กรัม)
    distance_km : int/float ตั้งแต่ 0 (กม.)
    express     : bool, True = ส่งด่วน
    """
    weight_g = _require_int(weight_g, "weight_g", 1, 30_000)
    distance = _require_non_negative_number(distance_km, "distance_km")
    express = _require_bool(express, "express")

    # ฐานราคา (สตางค์)
    if weight_g <= 1_000:
        fee = Fraction(4_000)                      # 40 บาท
    elif weight_g <= 5_000:
        fee = Fraction(8_000)                      # 80 บาท
    else:
        # 80 บาท + กิโลกรัมละ 15 บาท ตามสัดส่วนของกรัมที่เกิน 5,000
        # 15 บาท/กก. = 1500 สตางค์ / 1000 กรัม = 3/2 สตางค์ต่อกรัม
        fee = Fraction(8_000) + Fraction(weight_g - 5_000) * Fraction(3, 2)

    # ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (ค่า 100 พอดีไม่เกิน)
    if distance > 100:
        fee *= Fraction(6, 5)

    # ส่งด่วน คิดเพิ่ม 50% ต่อจากข้อก่อน
    if express:
        fee *= Fraction(3, 2)

    return _half_up(fee)


if __name__ == "__main__":
    print(shipping_fee(500, 10, False))     # 4000
    print(shipping_fee(1_500, 50, False))   # 8000
    print(shipping_fee(30_000, 150, True))  # 45500 * 1.2 * 1.5 = 81900
