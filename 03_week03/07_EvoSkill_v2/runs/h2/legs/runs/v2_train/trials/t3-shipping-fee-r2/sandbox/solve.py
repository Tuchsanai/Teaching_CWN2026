"""ค่าส่งเมล็ดกาแฟ BaanKafe

shipping_fee(weight_g, distance_km, express) -> int (หน่วยเป็นสตางค์)

กฎ:
1. ฐานตามน้ำหนัก (กรัม):
   - ไม่เกิน 1,000 กรัม           -> 40 บาท
   - ไม่เกิน 5,000 กรัม           -> 80 บาท
   - เกิน 5,000 กรัม              -> 80 บาท + (น้ำหนัก - 5,000) / 1,000 * 15 บาท (คิดตามสัดส่วนกรัม)
2. ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (คูณ 1.2)
3. ส่งด่วน (express=True) คิดเพิ่ม 50% (คูณ 1.5 ต่อจากข้อ 2)
4. ปัดเป็นสตางค์จำนวนเต็ม ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย

คำนวณด้วย Fraction ทั้งหมด (ไม่ใช้ float) และไม่มี side effect ตอน import
ผิดชนิดหรือนอกช่วง -> ValueError
"""

import math
from fractions import Fraction


# ---------- ตรวจข้อมูลนำเข้า ----------

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


# ---------- ปัดเศษ ----------

def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.5 -> 3, 2.4 -> 2"""
    return math.floor(Fraction(x) + Fraction(1, 2))


# ---------- ฟังก์ชันหลัก ----------

def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : int 1..30000 (กรัม)
    distance_km : ตัวเลข >= 0 (กิโลเมตร) รับ int หรือ float
    express     : True = ส่งด่วน, False = ส่งปกติ
    """
    w = _need_int(weight_g, "weight_g", low=1, high=30000)
    d = _need_number(distance_km, "distance_km", low=0)
    e = _need_bool(express, "express")

    # 1) ฐานตามน้ำหนัก (บาท, ยังไม่ปัด)
    if w <= 1000:
        fee = Fraction(40)
    elif w <= 5000:
        fee = Fraction(80)
    else:
        fee = Fraction(80) + Fraction(w - 5000, 1000) * 15

    # 2) ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (เกิน = > 100; 100 พอดีไม่เพิ่ม)
    if d > 100:
        fee *= Fraction(120, 100)

    # 3) ส่งด่วนคิดเพิ่ม 50% คูณต่อจากข้อก่อน
    if e:
        fee *= Fraction(150, 100)

    # 4) แปลงเป็นสตางค์ แล้วปัดครั้งเดียวตอนท้าย
    return _half_up(fee * 100)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(shipping_fee(800, 10, False))     # 4000 (40 บาท)
    print(shipping_fee(6000, 150, True))    # 17100 (171 บาท)
