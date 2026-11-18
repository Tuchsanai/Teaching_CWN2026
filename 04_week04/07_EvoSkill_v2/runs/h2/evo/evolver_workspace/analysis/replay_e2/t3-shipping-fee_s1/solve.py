"""ค่าส่งเมล็ดกาแฟ BaanKafe

shipping_fee(weight_g, distance_km, express) -> จำนวนเต็มสตางค์

กฎ (คำนวณเป็นสตางค์ด้วย Fraction ทั้งหมด ปัดครั้งเดียวตอนท้าย):
  1. น้ำหนัก <= 1,000 g        -> 40 บาท   (4000 สตางค์)
     1,000 < น้ำหนัก <= 5,000 g -> 80 บาท   (8000 สตางค์)
     น้ำหนัก > 5,000 g         -> 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน 5,000 g (คิดตามสัดส่วนกรัม)
  2. ระยะทาง > 100 km          -> คิดเพิ่ม 20% (ระยะทาง = 100 พอดี ไม่เพิ่ม)
  3. express = True            -> คิดเพิ่ม 50% (คูณต่อจากข้อ 2)
  4. ปัดครึ่งขึ้นเป็นสตางค์ (ค่าเริ่มต้นของ skill money-arithmetic-rounding เพราะลูกค้าเป็นผู้จ่าย)

ตรวจข้อมูลนำเข้า: ผิดชนิดหรือนอกช่วงให้ raise ValueError เสมอ
  weight_g    ต้องเป็น int จริง ช่วง 1..30000 (ไม่รับ bool, float, str)
  distance_km ต้องเป็นตัวเลข (int หรือ float) ตั้งแต่ 0 (ไม่รับ bool, str, nan, inf)
  express     ต้องเป็น True หรือ False จริง

ไม่มี side effect ตอน import
"""

import math
from fractions import Fraction


# ---------- ตรวจข้อมูลนำเข้า (คัดลอกจาก skill strict-input-validation) ----------

def _need_int(value, name, low=None, high=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


def _need_bool(value, name):
    """flag: ต้องเป็น True หรือ False จริง"""
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def _need_number(value, name, low=None):
    """ตัวเลขที่ไม่ใช่ bool: รับ int หรือ float แล้วแปลงเป็น Fraction ผ่าน str"""
    if type(value) not in (int, float):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    try:
        x = Fraction(str(value))
    except (ValueError, OverflowError) as exc:  # เช่น nan, inf
        raise ValueError(f"{name} ไม่ใช่ตัวเลขที่ใช้ได้") from exc
    if low is not None and x < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    return x


# ---------- ปัดเศษ (คัดลอกจาก skill money-arithmetic-rounding) ----------

def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


# ---------- ค่าคงที่ (หน่วยเป็นสตางค์) ----------

FEE_LIGHT = 4000          # 40 บาท, น้ำหนัก <= 1,000 g
FEE_BASE_HEAVY = 8000     # 80 บาท, น้ำหนัก 1,001 g ขึ้นไป (ฐานก่อนคิดส่วนเกิน 5,000 g)
EXTRA_PER_GRAM = Fraction(15 * 100, 1000)  # 15 บาท/กก. = 1500 สตางค์/1000 g = 1.5 สตางค์/g
LIGHT_MAX_G = 1000
HEAVY_THRESHOLD_G = 5000
FAR_KM = 100
FAR_MULT = Fraction(120, 100)     # +20%
EXPRESS_MULT = Fraction(150, 100)  # +50%


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    w = _need_int(weight_g, "weight_g", low=1, high=30000)
    d = _need_number(distance_km, "distance_km", low=0)
    e = _need_bool(express, "express")

    # 1) ฐานตามน้ำหนัก
    if w <= LIGHT_MAX_G:
        fee = Fraction(FEE_LIGHT)
    elif w <= HEAVY_THRESHOLD_G:
        fee = Fraction(FEE_BASE_HEAVY)
    else:
        fee = Fraction(FEE_BASE_HEAVY) + EXTRA_PER_GRAM * (w - HEAVY_THRESHOLD_G)

    # 2) ระยะทางเกิน 100 km เพิ่ม 20%
    if d > FAR_KM:
        fee *= FAR_MULT

    # 3) ส่งด่วนเพิ่ม 50% (คูณต่อจากข้อ 2)
    if e:
        fee *= EXPRESS_MULT

    # 4) ปัดครั้งเดียวตอนท้าย
    return _half_up(fee)


if __name__ == "__main__":
    print(shipping_fee(500, 10, False))     # 4000  (40 บาท)
    print(shipping_fee(5002, 101, True))    # 14405 (144.05 บาท)
    print(shipping_fee(30000, 250, True))
