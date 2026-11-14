"""ค่าส่งเมล็ดกาแฟ BaanKafe

ลำดับการคิด (ทำตามลำดับนี้ตรงตัว):
  1. ค่าส่งตามน้ำหนัก (หน่วยบาท, ใช้ Fraction เพื่อไม่คลาดจาก float)
       - w <= 1,000 กรัม            -> 40 บาท
       - 1,000 < w <= 5,000 กรัม     -> 80 บาท
       - w > 5,000 กรัม              -> 80 + 15 * (w - 5,000) / 1,000 บาท (คิดตามสัดส่วนกรัม)
  2. ระยะทางเกิน 100 กม. (d > 100)   -> คูณ 1.20
  3. ส่งด่วน (express = True)        -> คูณ 1.50 ต่อจากข้อ 2
  4. ผลลัพธ์เป็นจำนวนเต็มสตางค์      -> แปลงเป็นสตางค์ (x100) แล้วปัดครึ่งขึ้นครั้งเดียวที่ขั้นสุดท้าย

หมายเหตุการตีความ:
  - "เกิน 100 กม." ใช้ d > 100 (ที่ 100 พอดียังไม่คิดเพิ่ม)
  - ปัดเศษ: ปัดครึ่งขึ้น (half-up) ที่ขั้นสุดท้าย ไม่ใช่ banker's rounding
  - ค่าที่อยู่นอกช่วงที่โจทย์กำหนด (น้ำหนักนอก 1–30,000 กรัม หรือระยะทางติดลบ) จะ raise ValueError
"""

import math
from fractions import Fraction

SATANG_PER_BAHT = 100
MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30000


def _to_fraction(x):
    """แปลงค่าตัวเลขเป็น Fraction ผ่าน str เพื่อให้เลขทศนิยมที่เขียนไว้ เช่น 100.5 แม่นยำ"""
    if isinstance(x, Fraction):
        return x
    return Fraction(str(x))


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (int)

    weight_g    : น้ำหนักเป็นกรัม 1–30,000
    distance_km : ระยะทางเป็นกิโลเมตร (>= 0)
    express     : True = ส่งด่วน
    """
    w = _to_fraction(weight_g)
    d = _to_fraction(distance_km)

    if not (MIN_WEIGHT_G <= w <= MAX_WEIGHT_G):
        raise ValueError(f"weight_g ต้องอยู่ระหว่าง {MIN_WEIGHT_G:,}–{MAX_WEIGHT_G:,} กรัม")
    if d < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    # 1) ค่าส่งตามน้ำหนัก (บาท)
    if w <= 1000:
        fee = Fraction(40)
    elif w <= 5000:
        fee = Fraction(80)
    else:
        fee = Fraction(80) + Fraction(15) * (w - 5000) / 1000

    # 2) ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if d > 100:
        fee *= Fraction(120, 100)

    # 3) ส่งด่วนคิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
    if express:
        fee *= Fraction(150, 100)

    # 4) เป็นจำนวนเต็มสตางค์ ปัดครึ่งขึ้นครั้งเดียวที่ขั้นสุดท้าย
    satang = fee * SATANG_PER_BAHT
    return math.floor(satang + Fraction(1, 2))


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(shipping_fee(500, 10, False))     # 4000  (40 บาท)
    print(shipping_fee(5001, 10, False))    # 8002  (80.015 บาท -> 8001.5 สตางค์ -> ปัดขึ้น)
    print(shipping_fee(30000, 150, True))   # 81900 (819 บาท)
