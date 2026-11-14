"""ค่าส่งเมล็ดกาแฟ BaanKafe

กติกา (ทุกยอดเป็นสตางค์):
1. น้ำหนัก weight_g ต้องเป็นจำนวนเต็ม 1–30,000 กรัม
2. ฐานราคาตามน้ำหนัก:
   - ไม่เกิน 1,000 กรัม  -> 40 บาท
   - ไม่เกิน 5,000 กรัม  -> 80 บาท
   - เกิน 5,000 กรัม     -> 80 บาท + ส่วนที่เกิน 5,000 กรัม คิดกิโลกรัมละ 15 บาท (คิดตามสัดส่วนของกรัม)
3. ระยะทาง distance_km ต้องไม่ติดลบ ถ้าเกิน 100 กม. คิดเพิ่ม 20% ของยอดที่ได้จากข้อก่อน
4. ส่งด่วน (express=True) คิดเพิ่ม 50% ของยอดที่ได้จากข้อก่อน (คูณต่อจากข้อ 3)
5. คืนค่าส่งเป็นจำนวนเต็มสตางค์ ปัดครึ่งขึ้นครั้งเดียวตอนท้ายสุด
"""
from fractions import Fraction
import math


def _need_int(value, name, low=None, high=None):
    # bool ไม่นับเป็น int ที่นี่
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def _need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def _need_distance(value, name):
    # รับจำนวนจริงที่ไม่ใช่ bool, ไม่ติดลบ, ไม่ใช่ NaN/inf
    if type(value) not in (int, float, Fraction):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        raise ValueError(f"{name} ต้องเป็นตัวเลขจำกัด")
    if value < 0:
        raise ValueError(f"{name} ต้องไม่ติดลบ")
    return Fraction(value)


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ)"""
    return math.floor(Fraction(x) + Fraction(1, 2))


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    weight_g = _need_int(weight_g, "weight_g", 1, 30000)
    distance = _need_distance(distance_km, "distance_km")
    express = _need_bool(express, "express")

    # ฐานตามน้ำหนัก (สตางค์) คำนวณเป็น Fraction ทั้งหมด
    if weight_g <= 1000:
        fee = Fraction(40 * 100)
    elif weight_g <= 5000:
        fee = Fraction(80 * 100)
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 กรัม
        excess_g = weight_g - 5000
        fee = Fraction(80 * 100) + Fraction(excess_g * 1500, 1000)

    # ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if distance > 100:
        fee *= Fraction(120, 100)

    # ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
    if express:
        fee *= Fraction(150, 100)

    # ปัดครั้งเดียวตอนท้ายสุด
    return _half_up(fee)
