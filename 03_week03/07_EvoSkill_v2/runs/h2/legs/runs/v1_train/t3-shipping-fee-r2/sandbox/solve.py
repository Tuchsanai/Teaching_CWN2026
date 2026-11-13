"""ค่าส่งเมล็ดกาแฟ BaanKafe

shipping_fee(weight_g, distance_km, express) -> int (หน่วยเป็นสตางค์)

กติกาตามลำดับ:
1. ฐานตามน้ำหนัก
   - ไม่เกิน 1,000 กรัม  -> 40 บาท
   - ไม่เกิน 5,000 กรัม  -> 80 บาท
   - เกิน 5,000 กรัม     -> 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน 5,000 กรัม (คิดตามสัดส่วนของกรัม)
2. ระยะทางเกิน 100 กม. -> คูณ 1.20 (เพิ่ม 20%)
3. ส่งด่วน (express=True) -> คูณ 1.50 (เพิ่ม 50%) คูณต่อจากข้อ 2
4. ปัดครั้งเดียวที่ผลลัพธ์ เป็นจำนวนเต็มสตางค์ แบบปัดครึ่งขึ้น
"""

import math
from fractions import Fraction

BASE_LIGHT_BAHT = Fraction(40)        # น้ำหนัก <= 1,000 กรัม
BASE_MID_BAHT = Fraction(80)          # น้ำหนัก <= 5,000 กรัม
LIGHT_LIMIT_G = Fraction(1000)
MID_LIMIT_G = Fraction(5000)
MAX_WEIGHT_G = Fraction(30000)
EXTRA_PER_KG_BAHT = Fraction(15)      # ส่วนที่เกิน 5,000 กรัม ต่อ 1,000 กรัม
DISTANCE_LIMIT_KM = Fraction(100)
LONG_DISTANCE_MULT = Fraction(6, 5)   # +20%
EXPRESS_MULT = Fraction(3, 2)         # +50%


def _to_frac(x, name):
    """แปลงตัวเลขเป็น Fraction ผ่านข้อความ เพื่อไม่ให้เกิดคลาดเคลื่อนจาก float"""
    if isinstance(x, bool):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    try:
        return Fraction(str(x))
    except (ValueError, TypeError, ZeroDivisionError):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ค่าไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def shipping_fee(weight_g, distance_km, express):
    w = _to_frac(weight_g, "weight_g")
    d = _to_frac(distance_km, "distance_km")

    if not (1 <= w <= MAX_WEIGHT_G):
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1 ถึง 30000 กรัม")
    if d < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")
    if express not in (True, False):
        raise ValueError("express ต้องเป็น True หรือ False")

    # 1) ฐานตามน้ำหนัก (บาท)
    if w <= LIGHT_LIMIT_G:
        fee = BASE_LIGHT_BAHT
    elif w <= MID_LIMIT_G:
        fee = BASE_MID_BAHT
    else:
        fee = BASE_MID_BAHT + EXTRA_PER_KG_BAHT * (w - MID_LIMIT_G) / 1000

    # 2) ระยะทางเกิน 100 กม. เพิ่ม 20%
    if d > DISTANCE_LIMIT_KM:
        fee *= LONG_DISTANCE_MULT

    # 3) ส่งด่วน เพิ่ม 50% (ต่อจากข้อ 2)
    if express:
        fee *= EXPRESS_MULT

    # 4) แปลงเป็นสตางค์ แล้วปัดครั้งเดียว
    return _round_half_up(fee * 100)


if __name__ == "__main__":
    cases = [
        # (weight_g, distance_km, express, expected_satang)
        (500, 10, False, 4000),        # ฐาน 40
        (1000, 100, False, 4000),      # เท่ากับเกณฑ์ ไม่เกิน -> 40 และระยะ 100 ไม่เกิน 100
        (1001, 100, False, 8000),      # เกิน 1,000 -> 80
        (5000, 100, True, 12000),      # 80 * 1.5
        (5001, 0, False, 8002),        # 80.015 บาท = 8001.5 สตางค์ -> ปัดครึ่งขึ้น 8002
        (6000, 0, False, 9500),        # 80 + 15 = 95
        (6000, 101, False, 11400),     # 95 * 1.2 = 114
        (6000, 101, True, 17100),      # 114 * 1.5 = 171
        (2500, 120, True, 14400),      # 80 * 1.2 * 1.5 = 144
        (30000, 0, False, 45500),      # 80 + 15*25 = 455
        (30000, 150, True, 81900),     # 455 * 1.2 * 1.5 = 819
        (1000.0, 50.0, False, 4000),   # float ที่เป็นค่าเต็มก็รับได้
    ]
    for w, d, e, expected in cases:
        got = shipping_fee(w, d, e)
        assert got == expected, (w, d, e, got, expected)
        assert isinstance(got, int)

    for bad in [(0, 1, False), (30001, 1, False), (100, -1, False), (100, 1, "yes")]:
        try:
            shipping_fee(*bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {bad}")

    print("ผ่านทุกเคส:", len(cases), "เคส")
