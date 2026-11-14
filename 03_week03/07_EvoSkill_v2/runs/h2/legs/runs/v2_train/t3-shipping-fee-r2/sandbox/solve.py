"""ค่าส่งเมล็ดกาแฟ BaanKafe

shipping_fee(weight_g, distance_km, express) -> int (จำนวนเต็มสตางค์)

ลำดับการคิด:
1. ค่าส่งตามน้ำหนัก (บาท)
   - ไม่เกิน 1,000 กรัม            : 40 บาท
   - 1,001 ถึง 5,000 กรัม          : 80 บาท
   - เกิน 5,000 กรัม               : 80 บาท + 15 บาท ต่อกิโลกรัมของส่วนที่เกิน 5,000 กรัม
                                     (คิดตามสัดส่วนของกรัม ไม่ปัดเป็นกิโลกรัมเต็ม)
2. ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (คูณ 1.2 บนค่าส่งข้อ 1)
3. ส่งด่วน คิดเพิ่ม 50% คูณต่อจากข้อ 2 (คูณ 1.5)
4. ปัดลงเป็นจำนวนเต็มสตางค์ที่ขั้นสุดท้ายครั้งเดียว (โจทย์ไม่ได้ระบุวิธีปัด จึงใช้ค่าเริ่มต้นตัดเศษทิ้ง)
   คำนวณด้วย Fraction ทั้งหมดเพื่อไม่ให้ค่า float คลาด
"""

from fractions import Fraction
import math

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000

LIGHT_LIMIT_G = 1_000
MID_LIMIT_G = 5_000

LIGHT_FEE_BAHT = 40
MID_FEE_BAHT = 80
HEAVY_BASE_FEE_BAHT = 80
HEAVY_FEE_PER_KG_BAHT = 15

LONG_DISTANCE_KM = 100
LONG_DISTANCE_SURCHARGE = Fraction(120, 100)  # +20%
EXPRESS_SURCHARGE = Fraction(150, 100)        # +50%


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : น้ำหนักเป็นกรัม 1–30,000
    distance_km : ระยะทางเป็นกิโลเมตร (ตั้งแต่ 0)
    express     : True = ส่งด่วน
    """
    w = Fraction(weight_g)
    d = Fraction(distance_km)

    if w < MIN_WEIGHT_G or w > MAX_WEIGHT_G:
        raise ValueError(f"weight_g ต้องอยู่ระหว่าง {MIN_WEIGHT_G}–{MAX_WEIGHT_G} กรัม")
    if d < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    # 1) ค่าส่งตามน้ำหนัก (บาท)
    if w <= LIGHT_LIMIT_G:
        fee = Fraction(LIGHT_FEE_BAHT)
    elif w <= MID_LIMIT_G:
        fee = Fraction(MID_FEE_BAHT)
    else:
        excess_kg = (w - MID_LIMIT_G) / 1000
        fee = HEAVY_BASE_FEE_BAHT + excess_kg * HEAVY_FEE_PER_KG_BAHT

    # 2) ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (ต้องเกินจริง ค่าพอดี 100 ไม่เข้า)
    if d > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_SURCHARGE

    # 3) ส่งด่วน คิดเพิ่ม 50% คูณต่อจากข้อก่อน
    if express:
        fee *= EXPRESS_SURCHARGE

    # 4) ปัดลงเป็นสตางค์ครั้งเดียวที่ขั้นสุดท้าย
    return math.floor(fee * 100)


if __name__ == "__main__":
    print(shipping_fee(1000, 50, False))   # 4000
    print(shipping_fee(5001, 101, True))   # 14402
