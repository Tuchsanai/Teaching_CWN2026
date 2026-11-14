"""คิดค่าส่งเมล็ดกาแฟของ BaanKafe

หน่วยการคำนวณ: ใช้เศษส่วน (Fraction) ตลอดทาง ปัดครึ่งขึ้นครั้งเดียวที่ขั้นสุดท้าย
ผลลัพธ์เป็นจำนวนเต็มสตางค์ (1 บาท = 100 สตางค์)

ลำดับการคิด:
1. ค่าส่งฐานตามน้ำหนัก (หน่วยสตางค์)
   - น้ำหนัก <= 1,000 กรัม            -> 40 บาท
   - 1,000 < น้ำหนัก <= 5,000 กรัม    -> 80 บาท
   - น้ำหนัก > 5,000 กรัม             -> 80 บาท + 15 บาท ต่อ 1,000 กรัมของส่วนที่เกิน 5,000 (เป็นสัดส่วนตามกรัม)
2. ระยะทาง > 100 กม. คูณ 1.2 (ระยะทาง = 100 พอดี ไม่เข้า)
3. ส่งด่วน (express=True) คูณ 1.5 ต่อจากข้อ 2
4. ปัดครึ่งขึ้นเป็นสตางค์ที่ขั้นสุดท้าย
"""

from fractions import Fraction
import math

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000


def _base_fee_satang(weight_g):
    """ค่าส่งฐานตามน้ำหนัก คืนค่าเป็น Fraction หน่วยสตางค์"""
    if weight_g <= 1_000:
        return Fraction(40 * 100)
    if weight_g <= 5_000:
        return Fraction(80 * 100)
    # เกิน 5,000 กรัม: 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน (คิดตามสัดส่วนกรัม)
    extra_g = Fraction(weight_g) - 5_000
    return Fraction(80 * 100) + Fraction(15 * 100, 1_000) * extra_g


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเมล็ดกาแฟเป็นจำนวนเต็มสตางค์

    weight_g: น้ำหนักเป็นกรัม 1–30,000
    distance_km: ระยะทางเป็นกิโลเมตร (ตั้งแต่ 0)
    express: True คือส่งด่วน
    """
    if isinstance(weight_g, bool) or not (MIN_WEIGHT_G <= weight_g <= MAX_WEIGHT_G):
        raise ValueError(
            f"weight_g ต้องอยู่ในช่วง {MIN_WEIGHT_G}–{MAX_WEIGHT_G} กรัม ได้ {weight_g!r}"
        )
    if distance_km < 0:
        raise ValueError(f"distance_km ต้องไม่ติดลบ ได้ {distance_km!r}")

    fee = _base_fee_satang(weight_g)

    # ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if distance_km > 100:
        fee *= Fraction(120, 100)

    # ส่งด่วน คิดเพิ่ม 50% คูณต่อจากข้อก่อน
    if express:
        fee *= Fraction(150, 100)

    # ปัดครึ่งขึ้นที่ขั้นสุดท้าย (ค่าไม่ติดลบ)
    return math.floor(fee + Fraction(1, 2))
