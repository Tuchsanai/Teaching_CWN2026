"""ค่าส่งเมล็ดกาแฟ BaanKafe

shipping_fee(weight_g, distance_km, express) -> int (หน่วยเป็นสตางค์)

กติกา (ตามลำดับที่โจทย์ระบุ):
1. ค่าส่งตามน้ำหนัก (บาท)
   - ไม่เกิน 1,000 กรัม            -> 40 บาท
   - ไม่เกิน 5,000 กรัม            -> 80 บาท
   - เกิน 5,000 กรัม               -> 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน 5,000 กรัม
     (คิดตามสัดส่วนของกรัม ไม่ปัดเป็นก้อน)
2. ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (เกิน 100 พอดีไม่คิด)
3. ส่งด่วน (express=True) คิดเพิ่ม 50% คูณต่อจากข้อ 2
4. ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ครั้งเดียวตอนคืนค่า
"""

import math
from fractions import Fraction

WEIGHT_MIN_G = 1
WEIGHT_MAX_G = 30_000

LIGHT_LIMIT_G = 1_000
MID_LIMIT_G = 5_000

FEE_LIGHT_BAHT = Fraction(40)
FEE_MID_BAHT = Fraction(80)
PER_KG_OVER_MID_BAHT = Fraction(15)

LONG_DISTANCE_KM = Fraction(100)
LONG_DISTANCE_MULT = Fraction(6, 5)   # +20%
EXPRESS_MULT = Fraction(3, 2)         # +50%


def to_frac(x):
    """แปลงตัวเลขเป็น Fraction ผ่าน str เพื่อไม่ให้เกิดคลาดเคลื่อนจาก float"""
    return Fraction(str(x))


def round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ใช้ครั้งเดียวตอนคืนค่า ยอดไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def _is_number(x):
    return isinstance(x, (int, float, Fraction)) and not isinstance(x, bool)


def _weight_fee_baht(weight_g):
    """ค่าส่งตามน้ำหนัก เป็นบาท (Fraction)"""
    if weight_g <= LIGHT_LIMIT_G:
        return FEE_LIGHT_BAHT
    if weight_g <= MID_LIMIT_G:
        return FEE_MID_BAHT
    over_kg = (weight_g - MID_LIMIT_G) / Fraction(1000)
    return FEE_MID_BAHT + PER_KG_OVER_MID_BAHT * over_kg


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    if not _is_number(weight_g):
        raise ValueError("weight_g ต้องเป็นตัวเลข")
    if not _is_number(distance_km):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if express not in (True, False):
        raise ValueError("express ต้องเป็น True หรือ False")

    w = to_frac(weight_g)
    d = to_frac(distance_km)

    if not (WEIGHT_MIN_G <= w <= WEIGHT_MAX_G):
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1 ถึง 30,000 กรัม")
    if d < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    fee = _weight_fee_baht(w)            # 1. ตามน้ำหนัก
    if d > LONG_DISTANCE_KM:             # 2. ระยะทางเกิน 100 กม.
        fee *= LONG_DISTANCE_MULT
    if express is True:                  # 3. ส่งด่วน (ต่อจากข้อ 2)
        fee *= EXPRESS_MULT

    return round_half_up(fee * 100)      # 4. บาท -> สตางค์ ปัดครึ่งขึ้นครั้งเดียว


if __name__ == "__main__":
    cases = [
        # (weight_g, distance_km, express, expected_satang)
        (1, 0, False, 4000),                    # เบาสุด 40 บาท
        (1000, 50, False, 4000),                # เท่ากับเกณฑ์ 1,000 -> ยังเป็น 40
        (1001, 50, False, 8000),                # เกิน 1,000 -> 80
        (5000, 100, False, 8000),               # เท่ากับ 5,000 และระยะ 100 พอดี ไม่คิดเพิ่ม
        (5001, 100, False, 8002),               # 80.015 บาท -> 8001.5 สตางค์ -> ปัดขึ้น 8002
        (5000, 100.5, False, 9600),             # 80 * 1.2 = 96 บาท
        (5000, 100, True, 12000),               # 80 * 1.5 = 120 บาท
        (5000, 100.01, True, 14400),            # 80 * 1.2 * 1.5 = 144 บาท (ลำดับคูณไม่กระทบผล)
        (10000, 0, False, 15500),               # 80 + 5 * 15 = 155 บาท
        (30000, 0, False, 45500),               # 80 + 25 * 15 = 455 บาท
        (2500, 0, False, 8000),                 # 80 บาท (ไม่เกิน 5,000)
        (5500, 0, False, 8750),                 # 80 + 0.5 * 15 = 87.5 บาท
        (5001, 0, False, 8002),                 # ทดสอบซ้ำขอบเขต
        (5001, 200, True, 14403),               # 80.015 * 1.2 * 1.5 = 144.027 บาท -> 14402.7 -> 14403
    ]
    ok = True
    for w, d, e, exp in cases:
        got = shipping_fee(w, d, e)
        flag = "OK " if got == exp else "NG "
        if got != exp:
            ok = False
        print(f"{flag} weight={w} dist={d} express={e} -> {got} สตางค์ (คาดหวัง {exp})")
    print("ALL PASS" if ok else "SOME FAILED")
