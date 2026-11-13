"""คิดค่าส่งเมล็ดกาแฟของร้าน BaanKafe

กติกา (ทำตามลำดับ):
1. ค่าส่งพื้นฐานตามน้ำหนัก (หน่วยบาท)
   - ไม่เกิน 1,000 กรัม  -> 40 บาท
   - ไม่เกิน 5,000 กรัม  -> 80 บาท
   - เกิน 5,000 กรัม     -> 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน 5,000 กรัม
     (คิดตามสัดส่วนของกรัม ไม่ปัดเป็นกิโลกรัมเต็ม)
2. ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (คูณ 1.2)
3. ส่งด่วน คิดเพิ่ม 50% ต่อจากข้อ 2 (คูณ 1.5)
4. คืนค่าส่งเป็นจำนวนเต็มสตางค์ ปัดครึ่งขึ้นครั้งเดียวที่ผลลัพธ์สุดท้าย

ข้อสมมติฐานที่เลือกเอง:
- น้ำหนัก 1,001–5,000 กรัม ใช้อัตรา 80 บาท (ตามข้อ "ไม่เกิน 5,000 กรัม 80 บาท")
- "เกิน 100 กม." หมายถึง > 100 (ที่ 100 กม. พอดีไม่คิดเพิ่ม)
- ระยะทาง 0 ถือว่าใช้ได้
"""

import math
from fractions import Fraction

WEIGHT_MIN_G = 1
WEIGHT_MAX_G = 30_000

BASE_LIGHT_LIMIT_G = 1_000
BASE_STANDARD_LIMIT_G = 5_000

FEE_LIGHT_BAHT = Fraction(40)
FEE_STANDARD_BAHT = Fraction(80)
EXTRA_PER_KG_BAHT = Fraction(15)

LONG_DISTANCE_KM = Fraction(100)
LONG_DISTANCE_MULTIPLIER = Fraction(12, 10)  # +20%

EXPRESS_MULTIPLIER = Fraction(3, 2)  # +50%


def _to_frac(x, name):
    """แปลงตัวเลขเป็น Fraction โดยไม่ผ่าน float (กัน bool ด้วย)"""
    if isinstance(x, bool) or not isinstance(x, (int, float, Fraction)):
        raise TypeError(f"{name} ต้องเป็นตัวเลข ได้ {type(x).__name__}")
    return Fraction(str(x)) if isinstance(x, float) else Fraction(x)


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม ใช้ครั้งเดียวตอนคืนค่า (ค่าไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def _base_fee_baht(weight_g):
    """ค่าส่งพื้นฐานตามน้ำหนัก (บาท, Fraction)"""
    if weight_g <= BASE_LIGHT_LIMIT_G:
        return FEE_LIGHT_BAHT
    if weight_g <= BASE_STANDARD_LIMIT_G:
        return FEE_STANDARD_BAHT
    excess_g = weight_g - BASE_STANDARD_LIMIT_G
    return FEE_STANDARD_BAHT + EXTRA_PER_KG_BAHT * excess_g / 1000


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    น้ำหนักเป็นกรัม 1–30,000
    distance_km ระยะทางเป็นกิโลเมตร ตั้งแต่ 0
    express     True = ส่งด่วน
    """
    w = _to_frac(weight_g, "weight_g")
    d = _to_frac(distance_km, "distance_km")

    if not (WEIGHT_MIN_G <= w <= WEIGHT_MAX_G):
        raise ValueError(
            f"weight_g ต้องอยู่ระหว่าง {WEIGHT_MIN_G}–{WEIGHT_MAX_G} กรัม ได้ {weight_g}"
        )
    if d < 0:
        raise ValueError(f"distance_km ต้องไม่ติดลบ ได้ {distance_km}")

    fee = _base_fee_baht(w)

    if d > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_MULTIPLIER

    if express:
        fee *= EXPRESS_MULTIPLIER

    return _round_half_up(fee * 100)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(shipping_fee(2000, 50, False))   # 8000 สตางค์ (80 บาท)
    print(shipping_fee(6000, 50, False))   # 9500 สตางค์ (95 บาท)
    print(shipping_fee(6000, 150, True))   # 95 * 1.2 * 1.5 = 171 บาท -> 17100 สตางค์
