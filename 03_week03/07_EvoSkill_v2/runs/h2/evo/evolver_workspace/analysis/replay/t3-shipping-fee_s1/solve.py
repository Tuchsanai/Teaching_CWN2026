"""ค่าส่งเมล็ดกาแฟของ BaanKafe

กฎการคิดค่าส่ง:
- น้ำหนัก 1–30,000 กรัม
  - ไม่เกิน 1,000 กรัม  : 40 บาท
  - ไม่เกิน 5,000 กรัม  : 80 บาท
  - เกิน 5,000 กรัม     : 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน 5,000 กรัม (คิดตามสัดส่วนของกรัม)
- ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
- ส่งด่วน (express=True) คิดเพิ่ม 50% (คูณต่อจากระยะทาง)
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดเศษแบบครึ่งขึ้น)
"""

from fractions import Fraction

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000

# หน่วยเป็นสตางค์ (1 บาท = 100 สตางค์) เพื่อให้คำนวณเป็นจำนวนตรงตัวด้วย Fraction
_SATANG_PER_BAHT = 100


def _base_fee_satang(weight_g: int) -> Fraction:
    if weight_g <= 1_000:
        return Fraction(40 * _SATANG_PER_BAHT)
    if weight_g <= 5_000:
        return Fraction(80 * _SATANG_PER_BAHT)
    # 15 บาท/กก. = 15 * 100 สตางค์ / 1000 กรัม = 1.5 สตางค์ต่อกรัม
    excess_g = weight_g - 5_000
    return Fraction(80 * _SATANG_PER_BAHT) + Fraction(15 * _SATANG_PER_BAHT, 1000) * excess_g


def shipping_fee(weight_g: int, distance_km: float, express: bool) -> int:
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : น้ำหนักเป็นกรัม (1–30,000)
    distance_km : ระยะทางเป็นกิโลเมตร (>= 0)
    express     : True = ส่งด่วน
    """
    if isinstance(weight_g, bool) or not isinstance(weight_g, int):
        raise TypeError("weight_g ต้องเป็นจำนวนเต็ม (กรัม)")
    if not (MIN_WEIGHT_G <= weight_g <= MAX_WEIGHT_G):
        raise ValueError(f"weight_g ต้องอยู่ระหว่าง {MIN_WEIGHT_G} ถึง {MAX_WEIGHT_G} กรัม")

    distance = Fraction(str(distance_km))
    if distance < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    fee = _base_fee_satang(weight_g)

    if distance > 100:
        fee *= Fraction(120, 100)  # +20%

    if express:
        fee *= Fraction(150, 100)  # +50%

    # ปัดเศษแบบครึ่งขึ้นให้เป็นจำนวนเต็มสตางค์
    return int(fee + Fraction(1, 2))
