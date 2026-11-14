"""BaanKafe shipping fee calculator.

shipping_fee(weight_g, distance_km, express) -> int (จำนวนสตางค์)

กติกา
- น้ำหนัก 1–30,000 กรัม, ระยะทาง >= 0 กม., express=True คือส่งด่วน
- ฐานราคาตามน้ำหนัก:
    <= 1,000 g  -> 40 บาท
    <= 5,000 g  -> 80 บาท
    > 5,000 g   -> 80 บาท + (น้ำหนักส่วนเกิน 5,000 g) คิดกิโลกรัมละ 15 บาท (ตามสัดส่วนกรัม)
- ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (x1.2)
- ส่งด่วนคิดเพิ่ม 50% (x1.5) คูณต่อจากข้อก่อนหน้า
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ (ปัดเศษแบบ half-up)
"""

from decimal import Decimal, ROUND_HALF_UP

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000

LIGHT_LIMIT_G = Decimal("1000")
MEDIUM_LIMIT_G = Decimal("5000")

FEE_LIGHT = Decimal("40")
FEE_MEDIUM = Decimal("80")
RATE_PER_KG_OVER_MEDIUM = Decimal("15")  # บาทต่อกิโลกรัม

LONG_DISTANCE_KM = Decimal("100")
LONG_DISTANCE_MULTIPLIER = Decimal("1.2")
EXPRESS_MULTIPLIER = Decimal("1.5")


def _base_fee_baht(weight_g: Decimal) -> Decimal:
    if weight_g <= LIGHT_LIMIT_G:
        return FEE_LIGHT
    if weight_g <= MEDIUM_LIMIT_G:
        return FEE_MEDIUM
    excess_g = weight_g - MEDIUM_LIMIT_G
    return FEE_MEDIUM + (excess_g / Decimal("1000")) * RATE_PER_KG_OVER_MEDIUM


def shipping_fee(weight_g, distance_km, express) -> int:
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    weight = Decimal(str(weight_g))
    distance = Decimal(str(distance_km))

    if not (MIN_WEIGHT_G <= weight <= MAX_WEIGHT_G):
        raise ValueError(f"weight_g ต้องอยู่ในช่วง {MIN_WEIGHT_G}–{MAX_WEIGHT_G} กรัม")
    if distance < 0:
        raise ValueError("distance_km ต้องไม่ต่ำกว่า 0")

    fee = _base_fee_baht(weight)

    if distance > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_MULTIPLIER

    if express:
        fee *= EXPRESS_MULTIPLIER

    satang = (fee * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(satang)


if __name__ == "__main__":
    # ตัวอย่างการใช้งานเบื้องต้น
    print(shipping_fee(1000, 50, False))    # 4000  (40 บาท)
    print(shipping_fee(5000, 50, False))    # 8000  (80 บาท)
    print(shipping_fee(6000, 50, False))    # 9500  (95 บาท)
    print(shipping_fee(1000, 150, False))   # 4800  (48 บาท)
    print(shipping_fee(1000, 50, True))     # 6000  (60 บาท)
    print(shipping_fee(6000, 150, True))    # 17100 (171 บาท)
