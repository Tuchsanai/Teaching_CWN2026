"""ค่าส่งเมล็ดกาแฟ BaanKafe

shipping_fee(weight_g, distance_km, express) -> int (จำนวนเต็มสตางค์)

กติกา (คำนวณเป็นสตางค์ด้วย Fraction ปัดครั้งเดียวตอนท้ายแบบครึ่งขึ้น):
1. น้ำหนัก (weight_g) จำนวนเต็ม 1–30,000 กรัม
   - ไม่เกิน 1,000 g  -> 40 บาท (4,000 สตางค์)
   - ไม่เกิน 5,000 g  -> 80 บาท (8,000 สตางค์)
   - เกิน 5,000 g     -> 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน (คิดตามสัดส่วนกรัม)
2. ระยะทาง (distance_km) ตั้งแต่ 0 ถ้าเกิน 100 กม. คิดเพิ่ม 20% (×1.2)
3. ส่งด่วน (express=True) คิดเพิ่ม 50% (×1.5) คูณต่อจากข้อ 2

ข้อสมมติที่โจทย์ไม่ได้ระบุ:
- ปัดเศษ: ปัดครึ่งขึ้นเป็นสตางค์ (เงินที่ลูกค้าจ่ายเข้าร้าน)
- ระยะทาง "เกิน 100" หมายถึง > 100 (100 พอดีไม่คิดเพิ่ม)
- ผิดชนิดหรือนอกช่วง -> raise ValueError
"""

import math
from fractions import Fraction


# ---------- ตรวจข้อมูลนำเข้า (ผิดอะไรก็ ValueError) ----------

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
    """ตัวเลขที่ไม่ใช่ bool: int หรือ float -> Fraction ผ่าน str (ไม่มี error แบบ binary)"""
    if type(value) not in (int, float):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    try:
        x = Fraction(str(value))
    except (ValueError, OverflowError) as exc:  # เช่น nan, inf
        raise ValueError(f"{name} ไม่ใช่ตัวเลขที่ใช้ได้") from exc
    if low is not None and x < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    return x


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


# ---------- ฟังก์ชันหลัก ----------

def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    weight_g = _need_int(weight_g, "weight_g", low=1, high=30000)
    distance_km = _need_number(distance_km, "distance_km", low=0)
    express = _need_bool(express, "express")

    # 1) ค่าส่งตามน้ำหนัก (สตางค์, ยังไม่ปัด)
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์ / 1000 g = 3/2 สตางค์ต่อกรัม
        fee = Fraction(8000) + Fraction(3, 2) * (weight_g - 5000)

    # 2) ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if distance_km > 100:
        fee *= Fraction(6, 5)

    # 3) ส่งด่วนคิดเพิ่ม 50% (คูณต่อจากข้อ 2)
    if express:
        fee *= Fraction(3, 2)

    # ปัดครั้งเดียวตอนท้าย
    return _half_up(fee)


if __name__ == "__main__":
    print(shipping_fee(500, 10, False))     # 4000  (40 บาท)
    print(shipping_fee(5001, 0, False))     # 8002  (8001.5 -> ปัดครึ่งขึ้น)
    print(shipping_fee(30000, 150, True))   # 81900 (819 บาท)
