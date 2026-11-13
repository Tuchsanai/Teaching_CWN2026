"""ค่าส่งเมล็ดกาแฟ BaanKafe

ฟังก์ชัน shipping_fee(weight_g, distance_km, express) คืนค่าส่งเป็นจำนวนเต็มสตางค์

กติกา:
- น้ำหนัก 1–30,000 กรัม, ระยะทาง >= 0 กม.
- ฐานค่าส่งตามน้ำหนัก:
    * ไม่เกิน 1,000 กรัม  -> 40 บาท
    * ไม่เกิน 5,000 กรัม  -> 80 บาท
    * เกิน 5,000 กรัม     -> 80 บาท + กิโลกรัมละ 15 บาท ของส่วนที่เกิน 5,000 กรัม (คิดตามสัดส่วนของกรัม)
- ระยะทางเกิน 100 กม. -> คูณ 1.2 (เพิ่ม 20%)
- ส่งด่วน (express=True) -> คูณ 1.5 (เพิ่ม 50%) คูณต่อจากข้อก่อน

การปัดเศษ: คำนวณด้วย Decimal ในหน่วยสตางค์ แล้วปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์
"""

from decimal import Decimal, ROUND_HALF_UP

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000

SATANG_PER_BAHT = 100
# 15 บาท/กก. = 1,500 สตางค์ / 1,000 กรัม = 1.5 สตางค์ต่อกรัม
EXTRA_SATANG_PER_GRAM = Decimal("1.5")

LONG_DISTANCE_KM = 100
LONG_DISTANCE_MULTIPLIER = Decimal("1.2")
EXPRESS_MULTIPLIER = Decimal("1.5")


def _base_fee_satang(weight_g: Decimal) -> Decimal:
    if weight_g <= 1000:
        return Decimal(40 * SATANG_PER_BAHT)
    if weight_g <= 5000:
        return Decimal(80 * SATANG_PER_BAHT)
    return Decimal(80 * SATANG_PER_BAHT) + (weight_g - 5000) * EXTRA_SATANG_PER_GRAM


def shipping_fee(weight_g, distance_km, express) -> int:
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : น้ำหนัก (กรัม) 1–30,000
    distance_km : ระยะทาง (กม.) ตั้งแต่ 0
    express     : True = ส่งด่วน
    """
    weight = Decimal(str(weight_g))
    distance = Decimal(str(distance_km))

    if not (MIN_WEIGHT_G <= weight <= MAX_WEIGHT_G):
        raise ValueError(f"weight_g ต้องอยู่ระหว่าง {MIN_WEIGHT_G}–{MAX_WEIGHT_G} กรัม")
    if distance < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    fee = _base_fee_satang(weight)

    if distance > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_MULTIPLIER

    if express:
        fee *= EXPRESS_MULTIPLIER

    return int(fee.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    print(shipping_fee(500, 10, False))     # 4000  (40 บาท)
    print(shipping_fee(2000, 50, False))    # 8000  (80 บาท)
    print(shipping_fee(2000, 50, True))     # 12000 (120 บาท)
    print(shipping_fee(6000, 150, True))    # 17100 (171 บาท)
