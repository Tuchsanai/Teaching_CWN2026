"""ค่าส่งเมล็ดกาแฟ BaanKafe

shipping_fee(weight_g, distance_km, express) -> int (หน่วยเป็นสตางค์)

กติกา (ตามลำดับที่สเปกเขียน):
1. ค่าส่งฐานตามน้ำหนัก
   - ไม่เกิน 1,000 กรัม            -> 40 บาท
   - ไม่เกิน 5,000 กรัม            -> 80 บาท
   - เกิน 5,000 กรัม               -> 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน 5,000 กรัม
                                      (คิดตามสัดส่วนของกรัม)
2. ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (ระยะ 100 กม. พอดีไม่คิด)
3. ส่งด่วน (express=True) คิดเพิ่ม 50% คูณต่อจากข้อ 2
4. ผลลัพธ์เป็นจำนวนเต็มสตางค์ คำนวณด้วย Fraction แล้วปัดครึ่งขึ้นครั้งเดียวตอนท้าย

การตีความที่เลือกเอง:
- "ไม่เกิน 1,000 กรัม" รวม 1,000 พอดี ดังนั้น 1,001 กรัมจะเข้าช่วง 80 บาท
- "ไม่เกิน 5,000 กรัม" รวม 5,000 พอดี ดังนั้น 5,000 กรัมคิด 80 บาท (ไม่มีส่วนเกิน)
- ระยะทางรับเป็น int หรือ float ได้ (กม. อาจมีทศนิยม) แต่ต้องไม่ติดลบ และไม่เป็น NaN/inf
"""

import math
from fractions import Fraction


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม รับ int หรือ Fraction ที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def _require_weight(weight_g):
    if type(weight_g) is not int:
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม (กรัม)")
    if weight_g < 1 or weight_g > 30000:
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1 ถึง 30000 กรัม")
    return weight_g


def _require_distance(distance_km):
    if type(distance_km) not in (int, float):
        raise ValueError("distance_km ต้องเป็นตัวเลข (กิโลเมตร)")
    if math.isnan(distance_km) or math.isinf(distance_km):
        raise ValueError("distance_km ต้องเป็นจำนวนจำกัด")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")
    return Fraction(distance_km)


def _require_flag(express):
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น True หรือ False")
    return express


def shipping_fee(weight_g, distance_km, express):
    weight_g = _require_weight(weight_g)
    distance = _require_distance(distance_km)
    express = _require_flag(express)

    # 1) ค่าส่งฐานตามน้ำหนัก (หน่วยบาท เก็บเป็น Fraction ไม่ปัด)
    if weight_g <= 1000:
        fee = Fraction(40)
    elif weight_g <= 5000:
        fee = Fraction(80)
    else:
        extra_g = weight_g - 5000
        fee = Fraction(80) + Fraction(extra_g * 15, 1000)

    # 2) ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if distance > 100:
        fee *= Fraction(120, 100)

    # 3) ส่งด่วนคิดเพิ่ม 50% คูณต่อจากข้อ 2
    if express:
        fee *= Fraction(150, 100)

    # 4) แปลงเป็นสตางค์ แล้วปัดครึ่งขึ้นครั้งเดียว
    return _half_up(fee * 100)


if __name__ == "__main__":
    # ค่าที่คำนวณมือไว้ก่อน (หน่วยสตางค์)
    cases = [
        # (weight_g, distance_km, express, expected_satang)
        (500, 50, False, 4000),        # ฐาน 40 บาท
        (1000, 0, False, 4000),        # ขอบบน 1,000 กรัม ยังเป็น 40
        (1001, 0, False, 8000),        # เกิน 1,000 เป็น 80
        (5000, 100, False, 8000),      # ขอบ 5,000 และระยะ 100 พอดี ไม่คิดเพิ่ม
        (5001, 0, False, 8002),        # 80.015 บาท = 8001.5 สตางค์ ปัดครึ่งขึ้นเป็น 8002
        (30000, 0, False, 45500),      # 80 + 375 = 455 บาท
        (1000, 100.5, False, 4800),    # 40 * 1.2 = 48 บาท
        (1000, 0, True, 6000),         # 40 * 1.5 = 60 บาท
        (2000, 100, True, 12000),      # 80 * 1.5 = 120 บาท
        (30000, 101, True, 81900),     # 455 * 1.2 * 1.5 = 819 บาท
        (5001, 101, True, 14403),      # 80.015 * 1.8 = 144.027 บาท = 14402.7 สตางค์ ปัดเป็น 14403
    ]
    for w, d, e, expected in cases:
        got = shipping_fee(w, d, e)
        assert type(got) is int, (w, d, e, got)
        assert got == expected, f"w={w} d={d} express={e}: ได้ {got} คาดว่า {expected}"
    print(f"ทดสอบผ่าน {len(cases)} กรณี")
