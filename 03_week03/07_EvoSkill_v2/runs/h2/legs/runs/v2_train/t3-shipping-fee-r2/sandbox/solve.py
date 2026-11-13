"""ค่าส่งเมล็ดกาแฟ BaanKafe

shipping_fee(weight_g, distance_km, express) -> int (หน่วยเป็นสตางค์)

กติกาตามลำดับ:
1. ค่าส่งตามน้ำหนัก (บาท)
   - ไม่เกิน 1,000 กรัม            : 40 บาท
   - เกิน 1,000 ถึงไม่เกิน 5,000 กรัม: 80 บาท
   - เกิน 5,000 กรัม              : 80 บาท + (น้ำหนักที่เกิน 5,000 กรัม / 1,000) * 15 บาท
     (คิดตามสัดส่วนของกรัม ไม่ปัดเป็นกิโลกรัมเต็ม)
2. ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (คูณ 1.2)
3. ส่งด่วน (express=True) คิดเพิ่ม 50% ต่อจากข้อ 2 (คูณ 1.5)
4. คืนค่าเป็นจำนวนเต็มสตางค์ ปัดครึ่งขึ้นครั้งเดียวที่ผลสุดท้าย

การคำนวณใช้ fractions.Fraction เพื่อไม่ให้เกิดคลาดเคลื่อนจาก float
"""

import math
from fractions import Fraction

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000


def _to_frac(x):
    """แปลงค่าตัวเลขเป็น Fraction โดยไม่ผ่าน float (รองรับ int, float, Decimal, str ตัวเลข)"""
    if isinstance(x, bool):
        raise ValueError("ค่าต้องเป็นตัวเลข ไม่ใช่ bool")
    try:
        return Fraction(str(x))
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"ค่าไม่ใช่ตัวเลขที่ถูกต้อง: {x!r}") from exc


def _round_half_up(f):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (ค่าไม่ติดลบ)"""
    return math.floor(f + Fraction(1, 2))


def shipping_fee(weight_g, distance_km, express):
    """คำนวณค่าส่งเมล็ดกาแฟ คืนค่าเป็นจำนวนเต็มสตางค์"""
    weight = _to_frac(weight_g)
    distance = _to_frac(distance_km)

    if weight < MIN_WEIGHT_G or weight > MAX_WEIGHT_G:
        raise ValueError(f"น้ำหนักต้องอยู่ระหว่าง {MIN_WEIGHT_G}–{MAX_WEIGHT_G} กรัม: {weight_g!r}")
    if distance < 0:
        raise ValueError(f"ระยะทางต้องไม่ติดลบ: {distance_km!r}")

    # 1) ค่าส่งตามน้ำหนัก หน่วยเป็นบาท
    if weight <= 1000:
        fee = Fraction(40)
    elif weight <= 5000:
        fee = Fraction(80)
    else:
        fee = Fraction(80) + (weight - 5000) / 1000 * 15

    # 2) ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if distance > 100:
        fee *= Fraction(12, 10)

    # 3) ส่งด่วนคิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
    if express:
        fee *= Fraction(15, 10)

    # 4) แปลงเป็นสตางค์และปัดครึ่งขึ้นครั้งเดียว
    return _round_half_up(fee * 100)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(shipping_fee(1000, 50, False))   # 4000  (40 บาท)
    print(shipping_fee(3000, 50, False))   # 8000  (80 บาท)
    print(shipping_fee(6000, 50, False))   # 9500  (80 + 15 = 95 บาท)
    print(shipping_fee(3000, 150, True))   # 14400 (80 * 1.2 * 1.5 = 144 บาท)
