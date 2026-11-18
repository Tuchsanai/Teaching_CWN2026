"""คิดค่าส่งเมล็ดกาแฟของ BaanKafe (ผลลัพธ์เป็นสตางค์ จำนวนเต็ม)

กติกา:
1. ฐานตามน้ำหนัก (หน่วยสตางค์):
   - 1 ถึง 1,000 กรัม            -> 4,000 (40 บาท)
   - 1,001 ถึง 5,000 กรัม         -> 8,000 (80 บาท)
   - มากกว่า 5,000 กรัม           -> 8,000 + (กรัมที่เกิน 5,000) x 15 บาท/กก. (คิดตามสัดส่วนกรัม)
2. ระยะทางเกิน 100 กม. คูณ 1.20 (ระยะทาง 100 พอดี ไม่คิดเพิ่ม)
3. ส่งด่วน คูณ 1.50 ต่อจากข้อ 2
4. ปัดครั้งเดียวตอนท้าย เป็นจำนวนเต็มสตางค์ ด้วยการปัดครึ่งขึ้น
   (เป็นค่าที่ลูกค้าจ่ายเข้าร้าน ตามแนวทางใน skill money-arithmetic-rounding)

ไม่มี side effect ตอน import. ตัวอย่างการรันอยู่ใน if __name__ == "__main__".
"""

import math
from fractions import Fraction


# ---------- ตรวจข้อมูลนำเข้า (ผิดชนิดหรือนอกช่วง -> ValueError) ----------

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


# ---------- ปัดเศษ ----------

def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


# ---------- ฟังก์ชันหลัก ----------

def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g: จำนวนเต็ม 1–30,000 กรัม
    distance_km: ตัวเลขตั้งแต่ 0 (กม.)
    express: True = ส่งด่วน
    """
    weight_g = need_int(weight_g, "weight_g", low=1, high=30000)
    distance = need_number(distance_km, "distance_km", low=0)
    express = need_bool(express, "express")

    # 1) ฐานตามน้ำหนัก (ยังไม่ปัด)
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1,500 สตางค์ ต่อ 1,000 กรัม = 3/2 สตางค์ต่อกรัม
        fee = Fraction(8000) + Fraction(weight_g - 5000) * Fraction(1500, 1000)

    # 2) ระยะทางเกิน 100 กม. คูณ 1.20
    if distance > 100:
        fee *= Fraction(120, 100)

    # 3) ส่งด่วน คูณ 1.50 ต่อจากข้อก่อน
    if express:
        fee *= Fraction(150, 100)

    # 4) ปัดครั้งเดียวตอนท้าย
    return half_up(fee)


if __name__ == "__main__":
    print(shipping_fee(1000, 50, False))   # 4000  (40 บาท)
    print(shipping_fee(5001, 50, False))   # 8002  (80 บาท + 1.5 สต. ปัดครึ่งขึ้น)
    print(shipping_fee(30000, 150, True))  # 81900 (819 บาท)
