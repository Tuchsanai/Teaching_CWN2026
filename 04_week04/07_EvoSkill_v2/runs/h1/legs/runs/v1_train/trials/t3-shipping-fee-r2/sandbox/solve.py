"""คำนวณค่าส่งเมล็ดกาแฟของ BaanKafe เป็นจำนวนเต็มสตางค์"""

import math
from fractions import Fraction


def _require_weight(weight_g):
    if type(weight_g) is not int:
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม")
    if not (1 <= weight_g <= 30_000):
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1 ถึง 30000 กรัม")
    return weight_g


def _require_distance(distance_km):
    if type(distance_km) not in (int, float):  # ปฏิเสธ bool, str, None
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if not math.isfinite(distance_km) or distance_km < 0:
        raise ValueError("distance_km ต้องเป็นตัวเลขจำกัดและไม่ติดลบ")
    return Fraction(distance_km)  # แปลงเป็น Fraction ตรง ๆ ไม่ปัด


def _require_express(express):
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น True หรือ False")
    return express


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int, x ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    กฎ:
    1. ฐานตามน้ำหนัก: ไม่เกิน 1,000 ก. = 40 บาท, ไม่เกิน 5,000 ก. = 80 บาท,
       เกิน 5,000 ก. = 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน (คิดตามสัดส่วนกรัม)
    2. ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (ระยะ 100 พอดีไม่คิด)
    3. ส่งด่วนคิดเพิ่ม 50% คูณต่อจากข้อ 2
    4. ปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียวตอนท้าย
    """
    weight_g = _require_weight(weight_g)
    distance_km = _require_distance(distance_km)
    express = _require_express(express)

    if weight_g <= 1_000:
        fee = Fraction(40)
    elif weight_g <= 5_000:
        fee = Fraction(80)
    else:
        fee = Fraction(80) + Fraction(weight_g - 5_000, 1_000) * 15

    if distance_km > 100:
        fee *= Fraction(120, 100)

    if express:
        fee *= Fraction(150, 100)

    return _half_up(fee * 100)


if __name__ == "__main__":
    print(shipping_fee(500, 10, False))     # 4000
    print(shipping_fee(30_000, 150, True))  # 81900
