"""คิดค่าส่งเมล็ดกาแฟของ BaanKafe (ผลลัพธ์เป็นสตางค์ จำนวนเต็ม)"""
import math
from fractions import Fraction


def _require_int(value, name, low, high):
    if type(value) is not int:  # ปฏิเสธ bool, float, str, None
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if value < low or value > high:
        raise ValueError(f"{name} ต้องอยู่ระหว่าง {low} ถึง {high}")
    return value


def _require_distance(value):
    if type(value) not in (int, float):  # ปฏิเสธ bool, str, None
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if type(value) is float and not math.isfinite(value):
        raise ValueError("distance_km ต้องเป็นจำนวนจำกัด")
    if value < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")
    return Fraction(value)


def _require_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int (x ไม่ติดลบ)"""
    return int((x * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    weight_g = _require_int(weight_g, "weight_g", 1, 30_000)
    distance = _require_distance(distance_km)
    express = _require_bool(express, "express")

    # ฐานค่าส่ง เก็บเป็นสตางค์แบบ Fraction ยังไม่ปัด
    if weight_g <= 1_000:
        fee = Fraction(4_000)                      # 40 บาท
    elif weight_g <= 5_000:
        fee = Fraction(8_000)                      # 80 บาท
    else:
        # 80 บาท + 15 บาท/กก. ของส่วนที่เกิน 5,000 กรัม
        # 15 บาท/กก. = 1,500 สตางค์/1,000 กรัม = 3/2 สตางค์/กรัม
        fee = Fraction(8_000) + Fraction(weight_g - 5_000) * Fraction(3, 2)

    # ตัวคูณทบกันตามลำดับโจทย์ (ทั้งหมดคูณก่อนปัด)
    if distance > 100:                             # เกิน 100 กม. (100 พอดีไม่คิด)
        fee *= Fraction(6, 5)                      # +20%
    if express:
        fee *= Fraction(3, 2)                      # +50%

    # ปัดครั้งเดียวตอนท้าย (ไม่ได้ระบุ จึงใช้ half-up)
    return _half_up(fee)


if __name__ == "__main__":
    print(shipping_fee(1000, 50, False))   # 4000
    print(shipping_fee(6000, 120, True))   # 17100
