"""ค่าส่งเมล็ดกาแฟ BaanKafe

กติกา
- น้ำหนัก 1–30,000 กรัม
  - ไม่เกิน 1,000 กรัม : 40 บาท
  - ไม่เกิน 5,000 กรัม : 80 บาท
  - เกิน 5,000 กรัม    : 80 บาท + ส่วนที่เกิน 5,000 กรัม คิดกิโลกรัมละ 15 บาท (ตามสัดส่วนของกรัม)
- ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
- ส่งด่วน (express=True) คิดเพิ่ม 50% (คูณต่อจากข้อระยะทาง)
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดเศษแบบครึ่งขึ้น)
"""

from fractions import Fraction

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000

# หน่วยเป็นสตางค์ เพื่อให้คำนวณด้วยจำนวนเต็ม/เศษส่วนได้แม่นยำ
TIER_1_LIMIT_G = 1_000
TIER_2_LIMIT_G = 5_000
TIER_1_FEE_SATANG = 40 * 100
TIER_2_FEE_SATANG = 80 * 100
# 15 บาท/กก. = 1,500 สตางค์ / 1,000 กรัม = 3/2 สตางค์ต่อกรัม
OVER_TIER_2_SATANG_PER_G = Fraction(1500, 1000)

LONG_DISTANCE_KM = 100
LONG_DISTANCE_MULTIPLIER = Fraction(120, 100)
EXPRESS_MULTIPLIER = Fraction(150, 100)


def _base_fee_satang(weight_g: int) -> Fraction:
    if weight_g <= TIER_1_LIMIT_G:
        return Fraction(TIER_1_FEE_SATANG)
    if weight_g <= TIER_2_LIMIT_G:
        return Fraction(TIER_2_FEE_SATANG)
    excess_g = weight_g - TIER_2_LIMIT_G
    return TIER_2_FEE_SATANG + excess_g * OVER_TIER_2_SATANG_PER_G


def shipping_fee(weight_g, distance_km, express) -> int:
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : น้ำหนักเป็นกรัม (1–30,000)
    distance_km : ระยะทางเป็นกิโลเมตร (>= 0)
    express     : True = ส่งด่วน
    """
    if isinstance(weight_g, bool) or not isinstance(weight_g, (int, float)):
        raise TypeError("weight_g ต้องเป็นตัวเลข")
    if weight_g != int(weight_g):
        raise ValueError("weight_g ต้องเป็นจำนวนเต็มกรัม")
    weight_g = int(weight_g)
    if not MIN_WEIGHT_G <= weight_g <= MAX_WEIGHT_G:
        raise ValueError(f"weight_g ต้องอยู่ระหว่าง {MIN_WEIGHT_G}–{MAX_WEIGHT_G} กรัม")

    if isinstance(distance_km, bool) or not isinstance(distance_km, (int, float)):
        raise TypeError("distance_km ต้องเป็นตัวเลข")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    fee = _base_fee_satang(weight_g)

    # Fraction(float) ให้ค่าตรงกับตัวเลขที่รับเข้ามา จึงไม่เกิดความคลาดเคลื่อนจากทศนิยม
    if Fraction(distance_km) > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_MULTIPLIER

    if express:
        fee *= EXPRESS_MULTIPLIER

    # ปัดเศษครึ่งขึ้นให้เป็นจำนวนเต็มสตางค์
    return int(fee + Fraction(1, 2))


if __name__ == "__main__":
    print(shipping_fee(500, 10, False))      # 4000  (40.00 บาท)
    print(shipping_fee(3000, 50, False))     # 8000  (80.00 บาท)
    print(shipping_fee(6000, 50, False))     # 9500  (95.00 บาท)
    print(shipping_fee(6000, 150, True))     # 17100 (171.00 บาท)
