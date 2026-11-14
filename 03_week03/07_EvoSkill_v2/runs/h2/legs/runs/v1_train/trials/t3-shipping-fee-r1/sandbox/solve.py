"""คิดค่าส่งเมล็ดกาแฟของ BaanKafe

shipping_fee(weight_g, distance_km, express) -> จำนวนเต็ม หน่วยเป็นสตางค์

กฎ:
  1. น้ำหนัก (weight_g, 1–30,000 กรัม):
       ไม่เกิน 1,000 กรัม  -> 40 บาท
       ไม่เกิน 5,000 กรัม  -> 80 บาท
       เกิน 5,000 กรัม     -> 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน (คิดตามสัดส่วนกรัม)
  2. ระยะทาง (distance_km, ตั้งแต่ 0): เกิน 100 กม. คิดเพิ่ม 20%
  3. ส่งด่วน (express=True): คิดเพิ่ม 50% (คูณต่อจากข้อ 2)
  4. ปัดผลสุดท้ายครั้งเดียว แบบครึ่งขึ้น (ค่าส่งเป็นเงินที่ลูกค้าจ่าย)

การตีความที่โจทย์ไม่ได้ระบุ:
  - ระยะทางเกิน 100 กม. หมายถึง > 100 (ที่ 100 พอดีไม่คิดเพิ่ม)
  - ปัดครึ่งขึ้น เช่น 8001.5 สตางค์ -> 8002 สตางค์
"""
import math
from fractions import Fraction


# ---------- ตรวจข้อมูลนำเข้า (เข้มงวด: ผิดชนิดหรือนอกช่วง -> ValueError) ----------

def need_int(value, name, low=None, high=None):
    """จำนวนเต็มจริง: ไม่รับ bool, float, str"""
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if low is not None and value < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    if high is not None and value > high:
        raise ValueError(f"{name} ต้องไม่เกิน {high}")
    return value


def need_bool(value, name):
    """flag: ต้องเป็น True หรือ False จริง"""
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def need_number(value, name, low=None):
    """ตัวเลขที่ไม่ใช่ bool: รับ int หรือ float แล้วแปลงเป็น Fraction ผ่าน str
    เพื่อไม่ให้เกิดความคลาดเคลื่อนแบบ binary
    """
    if type(value) not in (int, float):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    try:
        x = Fraction(str(value))
    except (ValueError, OverflowError) as exc:  # เช่น nan, inf
        raise ValueError(f"{name} ไม่ใช่ตัวเลขที่ใช้ได้") from exc
    if low is not None and x < low:
        raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
    return x


# ---------- ปัดเศษ ----------

def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


# ---------- ค่าคงที่ (หน่วยสตางค์ = บาท * 100) ----------

BASE_LIGHT = 4000                 # 40 บาท, ไม่เกิน 1,000 กรัม
BASE_MEDIUM = 8000                # 80 บาท, ไม่เกิน 5,000 กรัม
EXTRA_PER_GRAM = Fraction(3, 2)   # 15 บาท/กก. = 1500 สตางค์ / 1000 กรัม = 1.5 สตางค์/กรัม
LONG_DISTANCE_KM = 100
LONG_DISTANCE_MULT = Fraction(120, 100)   # +20%
EXPRESS_MULT = Fraction(150, 100)         # +50%


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครั้งเดียวตอนท้าย)"""
    weight = need_int(weight_g, "weight_g", low=1, high=30000)
    distance = need_number(distance_km, "distance_km", low=0)
    is_express = need_bool(express, "express")

    # 1) ค่าส่งตามน้ำหนัก (ยังไม่ปัด)
    if weight <= 1000:
        fee = Fraction(BASE_LIGHT)
    elif weight <= 5000:
        fee = Fraction(BASE_MEDIUM)
    else:
        fee = BASE_MEDIUM + (weight - 5000) * EXTRA_PER_GRAM

    # 2) ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if distance > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_MULT

    # 3) ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อ 2)
    if is_express:
        fee *= EXPRESS_MULT

    # 4) ปัดครั้งเดียวตอนท้าย
    return half_up(fee)


if __name__ == "__main__":
    print("500 g, 50 km, ธรรมดา :", shipping_fee(500, 50, False), "สตางค์")
    print("5001 g, 101 km, ด่วน  :", shipping_fee(5001, 101, True), "สตางค์")
    print("30000 g, 200 km, ด่วน :", shipping_fee(30000, 200, True), "สตางค์")
