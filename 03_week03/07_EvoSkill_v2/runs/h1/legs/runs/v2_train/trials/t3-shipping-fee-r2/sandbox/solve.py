"""คิดค่าส่งเมล็ดกาแฟของ BaanKafe

กฎ (ตามโจทย์):
1. น้ำหนัก (weight_g): จำนวนเต็ม 1–30,000 กรัม
   - ไม่เกิน 1,000 กรัม          -> 40 บาท
   - ไม่เกิน 5,000 กรัม          -> 80 บาท
   - เกิน 5,000 กรัม             -> 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน 5,000 กรัม
     (คิดตามสัดส่วนของกรัม)
2. ระยะทาง (distance_km): ตั้งแต่ 0 ขึ้นไป ถ้าเกิน 100 กม. คิดเพิ่ม 20%
3. ส่งด่วน (express=True): คิดเพิ่ม 50% คูณต่อจากข้อ 2
4. ผลลัพธ์เป็นจำนวนเต็มสตางค์

การคำนวณ:
- ใช้ Fraction ตลอด ไม่มี float ในการคำนวณ
- ปัดเศษครั้งเดียวตอนท้าย แบบครึ่งขึ้น (half-up) เพราะเป็นเงินที่ลูกค้าจ่ายให้ร้าน
"""

import math
from fractions import Fraction

WEIGHT_MIN_G = 1
WEIGHT_MAX_G = 30_000
BASE_LIGHT_THRESHOLD_G = 1_000
BASE_MEDIUM_THRESHOLD_G = 5_000
FEE_LIGHT_SATANG = 40 * 100
FEE_MEDIUM_SATANG = 80 * 100
EXTRA_PER_KG_BAHT = 15
LONG_DISTANCE_KM = 100
LONG_DISTANCE_MULTIPLIER = Fraction(12, 10)  # +20%
EXPRESS_MULTIPLIER = Fraction(15, 10)        # +50%


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int, x ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def _validate(weight_g, distance_km, express):
    if type(weight_g) is not int:
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม (int)")
    if not (WEIGHT_MIN_G <= weight_g <= WEIGHT_MAX_G):
        raise ValueError(f"weight_g ต้องอยู่ระหว่าง {WEIGHT_MIN_G} ถึง {WEIGHT_MAX_G} กรัม")

    if type(distance_km) not in (int, float):
        raise ValueError("distance_km ต้องเป็นตัวเลข (int หรือ float)")
    if not math.isfinite(distance_km):
        raise ValueError("distance_km ต้องเป็นจำนวนจำกัด")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    if type(express) is not bool:
        raise ValueError("express ต้องเป็น True หรือ False")


def _base_fee_satang(weight_g):
    """ค่าส่งฐานตามน้ำหนัก เป็นสตางค์ (Fraction ยังไม่ปัด)"""
    if weight_g <= BASE_LIGHT_THRESHOLD_G:
        return Fraction(FEE_LIGHT_SATANG)
    if weight_g <= BASE_MEDIUM_THRESHOLD_G:
        return Fraction(FEE_MEDIUM_SATANG)
    excess_g = weight_g - BASE_MEDIUM_THRESHOLD_G
    extra_baht = Fraction(excess_g, 1000) * EXTRA_PER_KG_BAHT
    return FEE_MEDIUM_SATANG + extra_baht * 100


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเมล็ดกาแฟเป็นจำนวนเต็มสตางค์

    weight_g: น้ำหนักเป็นกรัม (int, 1–30,000)
    distance_km: ระยะทางเป็นกิโลเมตร (0 ขึ้นไป)
    express: True ถ้าส่งด่วน
    """
    _validate(weight_g, distance_km, express)

    fee = _base_fee_satang(weight_g)

    if Fraction(distance_km) > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_MULTIPLIER

    if express:
        fee *= EXPRESS_MULTIPLIER

    return _half_up(fee)


if __name__ == "__main__":
    examples = [
        (500, 10, False),
        (1000, 10, False),
        (1001, 10, False),
        (5000, 10, False),
        (5001, 10, False),
        (6000, 10, False),
        (30000, 10, False),
        (1500, 100, False),
        (1500, 100.5, False),
        (1500, 10, True),
        (6000, 150, True),
    ]
    for w, d, e in examples:
        print(f"weight_g={w:>6} distance_km={d:>6} express={e!s:<5} -> {shipping_fee(w, d, e)} สตางค์")
