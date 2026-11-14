"""ค่าส่งเมล็ดกาแฟของ BaanKafe

shipping_fee(weight_g, distance_km, express) -> จำนวนเต็มสตางค์

กฎ (ตามโจทย์):
1. น้ำหนัก (weight_g, จำนวนเต็ม 1–30,000 กรัม):
   - ไม่เกิน 1,000 กรัม          -> 40 บาท
   - 1,001–5,000 กรัม           -> 80 บาท
   - เกิน 5,000 กรัม            -> 80 บาท + (กรัมที่เกิน 5,000) * 15 บาท/กก. (คิดตามสัดส่วนของกรัม)
2. ระยะทาง (distance_km, ตั้งแต่ 0): เกิน 100 กม. คิดเพิ่ม 20% ของค่าส่งจากข้อ 1
3. ส่งด่วน (express=True): คิดเพิ่ม 50% คูณต่อจากข้อ 2
4. คำนวณทั้งหมดเป็น Fraction แล้วปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียวตอนท้าย
   (เงินที่ลูกค้าจ่ายเข้าร้าน จึงใช้ปัดครึ่งขึ้นตามหลัก skill money-arithmetic-rounding)

ข้อมูลนำเข้าที่ผิดชนิดหรือนอกช่วง -> raise ValueError เท่านั้น
"""

import math
from fractions import Fraction

# ค่าคงที่ (หน่วยสตางค์)
BASE_LIGHT_SATANG = 4000     # ไม่เกิน 1,000 กรัม = 40 บาท
BASE_MEDIUM_SATANG = 8000    # 1,001–5,000 กรัม และฐานของกรณีเกิน 5,000 กรัม = 80 บาท
EXTRA_PER_KG_SATANG = 1500   # 15 บาท/กก. สำหรับส่วนที่เกิน 5,000 กรัม
MAX_WEIGHT_G = 30_000
LIGHT_LIMIT_G = 1_000
MEDIUM_LIMIT_G = 5_000
DISTANCE_LIMIT_KM = 100
DISTANCE_SURCHARGE = Fraction(120, 100)  # +20%
EXPRESS_SURCHARGE = Fraction(150, 100)   # +50%


# ---------- ตรวจข้อมูลนำเข้า (ValueError เท่านั้น) ----------

def _need_int(value, name, low, high):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if value < low or value > high:
        raise ValueError(f"{name} ต้องอยู่ระหว่าง {low} ถึง {high}")
    return value


def _need_bool(value, name):
    """flag: ต้องเป็น True หรือ False จริง"""
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def _need_nonneg_number(value, name):
    """ตัวเลขไม่ติดลบ (int หรือ float, ไม่รับ bool/str) แปลงเป็น Fraction ผ่าน str
    เพื่อไม่ให้เกิดความคลาดเคลื่อนแบบ binary ของ float
    """
    if type(value) not in (int, float):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    try:
        x = Fraction(str(value))
    except (ValueError, OverflowError) as exc:  # เช่น nan, inf
        raise ValueError(f"{name} ไม่ใช่ตัวเลขที่ใช้ได้") from exc
    if x < 0:
        raise ValueError(f"{name} ต้องไม่ติดลบ")
    return x


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(x + Fraction(1, 2))


# ---------- ฟังก์ชันหลัก ----------

def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    weight_g = _need_int(weight_g, "weight_g", 1, MAX_WEIGHT_G)
    distance_km = _need_nonneg_number(distance_km, "distance_km")
    express = _need_bool(express, "express")

    # 1) ค่าส่งตามน้ำหนัก (ยังไม่ปัด)
    if weight_g <= LIGHT_LIMIT_G:
        fee = Fraction(BASE_LIGHT_SATANG)
    elif weight_g <= MEDIUM_LIMIT_G:
        fee = Fraction(BASE_MEDIUM_SATANG)
    else:
        extra_g = weight_g - MEDIUM_LIMIT_G
        fee = Fraction(BASE_MEDIUM_SATANG) + Fraction(extra_g * EXTRA_PER_KG_SATANG, 1000)

    # 2) ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (คูณต่อจากข้อก่อน)
    if distance_km > DISTANCE_LIMIT_KM:
        fee *= DISTANCE_SURCHARGE

    # 3) ส่งด่วนคิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
    if express:
        fee *= EXPRESS_SURCHARGE

    # 4) ปัดครั้งเดียวตอนท้าย
    return _half_up(fee)


if __name__ == "__main__":
    examples = [
        (500, 10, False),
        (1000, 0, False),
        (5001, 0, False),
        (5001, 0, True),
        (30000, 0, False),
        (2000, 101, True),
    ]
    for w, d, e in examples:
        print(f"weight_g={w} distance_km={d} express={e} -> {shipping_fee(w, d, e)} สตางค์")
