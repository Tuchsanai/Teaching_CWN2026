"""ค่าส่งเมล็ดกาแฟ BaanKafe

คำนวณค่าส่งเป็น "สตางค์" (จำนวนเต็ม) โดยใช้ Decimal เพื่อหลีกเลี่ยง
ความคลาดเคลื่อนของ float
"""

from decimal import Decimal, ROUND_HALF_UP

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000
EXPRESS_MULTIPLIER = Decimal("1.5")
LONG_DISTANCE_KM = 100
LONG_DISTANCE_MULTIPLIER = Decimal("1.2")


def _base_fee_baht(weight_g: int) -> Decimal:
    """ค่าส่งพื้นฐานตามน้ำหนัก (บาท)"""
    if weight_g <= 1_000:
        return Decimal(40)
    if weight_g <= 5_000:
        return Decimal(80)
    # เกิน 5,000 กรัม: 80 บาท + ส่วนที่เกิน คิดกิโลกรัมละ 15 บาท ตามสัดส่วนกรัม
    excess_g = Decimal(weight_g - 5_000)
    return Decimal(80) + excess_g / Decimal(1_000) * Decimal(15)


def shipping_fee(weight_g: int, distance_km: float, express: bool) -> int:
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : น้ำหนัก 1–30,000 กรัม
    distance_km : ระยะทาง (ตั้งแต่ 0 กม.)
    express     : True = ส่งด่วน (คิดเพิ่ม 50%)
    """
    if isinstance(weight_g, bool) or not isinstance(weight_g, (int, Decimal)):
        raise TypeError("weight_g ต้องเป็นจำนวนเต็ม (กรัม)")
    if not (MIN_WEIGHT_G <= weight_g <= MAX_WEIGHT_G):
        raise ValueError(f"weight_g ต้องอยู่ระหว่าง {MIN_WEIGHT_G}–{MAX_WEIGHT_G} กรัม")
    distance = Decimal(str(distance_km))
    if distance < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    fee = _base_fee_baht(int(weight_g))

    # ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if distance > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_MULTIPLIER

    # ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อนหน้า)
    if express:
        fee *= EXPRESS_MULTIPLIER

    # แปลงเป็นสตางค์และปัดเป็นจำนวนเต็ม (ปัดครึ่งขึ้น)
    satang = (fee * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(satang)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(shipping_fee(500, 10, False))     # 4000  (40 บาท)
    print(shipping_fee(3_000, 50, True))    # 12000 (80 × 1.5 = 120 บาท)
    print(shipping_fee(7_000, 150, False))  # 13200 ((80+30) × 1.2 = 132 บาท)
    print(shipping_fee(7_000, 150, True))   # 19800 (132 × 1.5 = 198 บาท)
