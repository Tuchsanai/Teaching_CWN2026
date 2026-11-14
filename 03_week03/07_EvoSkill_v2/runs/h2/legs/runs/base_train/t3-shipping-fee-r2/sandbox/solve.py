"""คำนวณค่าส่งเมล็ดกาแฟของร้าน BaanKafe

กติกา
- น้ำหนัก 1–30,000 กรัม, ระยะทาง >= 0 กม., express=True คือส่งด่วน
- ค่าส่งฐานตามน้ำหนัก:
  - ไม่เกิน 1,000 กรัม  -> 40 บาท
  - ไม่เกิน 5,000 กรัม  -> 80 บาท
  - เกิน 5,000 กรัม     -> 80 บาท + (น้ำหนักที่เกิน 5,000 กรัม) ตามสัดส่วน กิโลกรัมละ 15 บาท
- ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
- ส่งด่วนคิดเพิ่ม 50% (คูณต่อจากข้อระยะทาง)
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดเศษแบบครึ่งขึ้น)
"""

from fractions import Fraction

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000

SATANG_PER_BAHT = 100

# คำนวณทั้งหมดเป็นสตางค์ด้วย Fraction เพื่อไม่ให้มีข้อผิดพลาดจากทศนิยมของ float
BASE_TIER_1_SATANG = 40 * SATANG_PER_BAHT   # ไม่เกิน 1,000 กรัม
BASE_TIER_2_SATANG = 80 * SATANG_PER_BAHT   # ไม่เกิน 5,000 กรัม
TIER_1_LIMIT_G = 1_000
TIER_2_LIMIT_G = 5_000
# 15 บาท/กก. = 1,500 สตางค์ / 1,000 กรัม = 1.5 สตางค์ต่อกรัม
EXTRA_SATANG_PER_G = Fraction(15 * SATANG_PER_BAHT, 1000)

LONG_DISTANCE_KM = 100
LONG_DISTANCE_MULTIPLIER = Fraction(6, 5)   # +20%
EXPRESS_MULTIPLIER = Fraction(3, 2)         # +50%


def _base_fee_satang(weight_g: int) -> Fraction:
    if weight_g <= TIER_1_LIMIT_G:
        return Fraction(BASE_TIER_1_SATANG)
    if weight_g <= TIER_2_LIMIT_G:
        return Fraction(BASE_TIER_2_SATANG)
    excess_g = weight_g - TIER_2_LIMIT_G
    return BASE_TIER_2_SATANG + excess_g * EXTRA_SATANG_PER_G


def shipping_fee(weight_g, distance_km, express) -> int:
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g: น้ำหนักเป็นกรัม (1–30,000)
    distance_km: ระยะทางเป็นกิโลเมตร (>= 0)
    express: True คือส่งด่วน
    """
    if isinstance(weight_g, bool) or not isinstance(weight_g, (int, float, Fraction)):
        raise TypeError("weight_g must be a number")
    if not (MIN_WEIGHT_G <= weight_g <= MAX_WEIGHT_G):
        raise ValueError(f"weight_g must be between {MIN_WEIGHT_G} and {MAX_WEIGHT_G}")
    if isinstance(distance_km, bool) or not isinstance(distance_km, (int, float, Fraction)):
        raise TypeError("distance_km must be a number")
    if distance_km < 0:
        raise ValueError("distance_km must be >= 0")

    fee = _base_fee_satang(Fraction(weight_g))

    if distance_km > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_MULTIPLIER

    if express:
        fee *= EXPRESS_MULTIPLIER

    # ปัดเศษครึ่งขึ้น (half-up) เป็นสตางค์จำนวนเต็ม
    return int(fee + Fraction(1, 2)) if fee >= 0 else int(fee - Fraction(1, 2))


if __name__ == "__main__":
    examples = [
        (500, 10, False),     # 4000 สตางค์ = 40.00
        (1000, 10, False),    # 4000
        (1001, 10, False),    # 8000
        (5000, 10, False),    # 8000
        (6000, 10, False),    # 8000 + 1000*1.5 = 9500
        (30000, 10, False),   # 8000 + 25000*1.5 = 45500
        (1000, 150, False),   # 4000 * 1.2 = 4800
        (1000, 100, False),   # ไม่เกิน 100 กม. -> 4000
        (1000, 10, True),     # 4000 * 1.5 = 6000
        (6000, 150, True),    # 9500 * 1.2 * 1.5 = 17100
    ]
    for w, d, e in examples:
        print(f"weight={w:>5} g, distance={d:>4} km, express={str(e):<5} -> {shipping_fee(w, d, e)} สตางค์")
