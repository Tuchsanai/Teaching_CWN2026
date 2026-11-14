"""ค่าส่งเมล็ดกาแฟของ BaanKafe

shipping_fee(weight_g, distance_km, express) -> int (จำนวนสตางค์)

กติกา:
- ฐานตามน้ำหนัก
  - ไม่เกิน 1,000 กรัม  -> 40 บาท
  - ไม่เกิน 5,000 กรัม  -> 80 บาท
  - เกิน 5,000 กรัม     -> 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน (คิดตามสัดส่วนของกรัม)
- ระยะทางเกิน 100 กม. คิดเพิ่ม 20%  (x 1.2)
- ส่งด่วน คิดเพิ่ม 50%              (x 1.5, คูณต่อจากข้อก่อน)
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดเศษแบบครึ่งขึ้น)

คำนวณด้วย Fraction เพื่อไม่ให้เกิดความคลาดเคลื่อนของ float
"""

from fractions import Fraction
import math

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000

BASE_LIGHT_SATANG = 40 * 100      # ไม่เกิน 1,000 กรัม
BASE_MEDIUM_SATANG = 80 * 100     # ไม่เกิน 5,000 กรัม (และฐานของช่วงเกิน 5,000 กรัม)
EXTRA_PER_KG_SATANG = 15 * 100    # ส่วนเกิน 5,000 กรัม: 15 บาท/กก.

LONG_DISTANCE_KM = 100
LONG_DISTANCE_MULTIPLIER = Fraction(6, 5)   # +20%
EXPRESS_MULTIPLIER = Fraction(3, 2)         # +50%


def _base_fee_satang(weight_g: Fraction) -> Fraction:
    if weight_g <= 1000:
        return Fraction(BASE_LIGHT_SATANG)
    if weight_g <= 5000:
        return Fraction(BASE_MEDIUM_SATANG)
    over_g = weight_g - 5000
    return BASE_MEDIUM_SATANG + over_g * EXTRA_PER_KG_SATANG / 1000


def shipping_fee(weight_g, distance_km, express) -> int:
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    weight = Fraction(weight_g)
    distance = Fraction(distance_km)

    if not (MIN_WEIGHT_G <= weight <= MAX_WEIGHT_G):
        raise ValueError(f"weight_g ต้องอยู่ระหว่าง {MIN_WEIGHT_G}-{MAX_WEIGHT_G} กรัม")
    if distance < 0:
        raise ValueError("distance_km ต้องไม่ต่ำกว่า 0")

    fee = _base_fee_satang(weight)

    if distance > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_MULTIPLIER

    if express:
        fee *= EXPRESS_MULTIPLIER

    # ปัดเศษครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (ค่าไม่ติดลบ)
    return math.floor(fee + Fraction(1, 2))


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน (หน่วยเป็นสตางค์)
    print(shipping_fee(500, 10, False))      # 4000  = 40.00 บาท
    print(shipping_fee(1000, 10, False))     # 4000  = 40.00 บาท
    print(shipping_fee(1001, 10, False))     # 8000  = 80.00 บาท
    print(shipping_fee(5000, 10, False))     # 8000  = 80.00 บาท
    print(shipping_fee(6000, 150, False))    # 11400 = 114.00 บาท (95 x 1.2)
    print(shipping_fee(6000, 150, True))     # 17100 = 171.00 บาท (95 x 1.2 x 1.5)
    print(shipping_fee(30000, 0, True))      # 80 + 25*15 = 455 บาท x 1.5 = 682.50 บาท -> 68250
