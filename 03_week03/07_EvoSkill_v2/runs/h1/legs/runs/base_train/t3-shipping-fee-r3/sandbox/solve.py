"""ค่าส่งเมล็ดกาแฟ BaanKafe

shipping_fee(weight_g, distance_km, express) -> int (หน่วยเป็นสตางค์)

กติกา:
- ฐานตามน้ำหนัก:
    ไม่เกิน 1,000 กรัม  -> 40 บาท
    ไม่เกิน 5,000 กรัม  -> 80 บาท
    เกิน 5,000 กรัม     -> 80 บาท + 15 บาท/กก. ของส่วนที่เกิน 5,000 กรัม (คิดตามสัดส่วนกรัม)
- ระยะทางเกิน 100 กม. -> คิดเพิ่ม 20% (เกิน 100 จริง ๆ; 100 กม. พอดีไม่เพิ่ม)
- ส่งด่วน (express=True) -> คิดเพิ่ม 50% คูณต่อจากข้อก่อนหน้า
- ผลลัพธ์ปัดเศษเป็นสตางค์จำนวนเต็ม (ปัดครึ่งขึ้น)
"""

from decimal import Decimal, ROUND_HALF_UP

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000

BASE_LIGHT_SATANG = 4000     # 40 บาท
BASE_MEDIUM_SATANG = 8000    # 80 บาท
EXCESS_PER_KG_SATANG = 1500  # 15 บาท/กก.

LIGHT_LIMIT_G = 1_000
MEDIUM_LIMIT_G = 5_000

FAR_DISTANCE_KM = 100
FAR_SURCHARGE = Decimal("1.20")
EXPRESS_SURCHARGE = Decimal("1.50")


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    if isinstance(weight_g, bool) or not isinstance(weight_g, (int, float)):
        raise TypeError("weight_g ต้องเป็นตัวเลข")
    if not (MIN_WEIGHT_G <= weight_g <= MAX_WEIGHT_G):
        raise ValueError(f"weight_g ต้องอยู่ระหว่าง {MIN_WEIGHT_G}–{MAX_WEIGHT_G} กรัม")
    if isinstance(distance_km, bool) or not isinstance(distance_km, (int, float)):
        raise TypeError("distance_km ต้องเป็นตัวเลข")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ต่ำกว่า 0")

    # คำนวณเป็นสตางค์ด้วย Decimal เพื่อหลีกเลี่ยงความคลาดเคลื่อนของ float
    weight = Decimal(str(weight_g))
    if weight <= LIGHT_LIMIT_G:
        fee = Decimal(BASE_LIGHT_SATANG)
    elif weight <= MEDIUM_LIMIT_G:
        fee = Decimal(BASE_MEDIUM_SATANG)
    else:
        excess_g = weight - MEDIUM_LIMIT_G
        fee = Decimal(BASE_MEDIUM_SATANG) + Decimal(EXCESS_PER_KG_SATANG) * excess_g / Decimal(1000)

    if Decimal(str(distance_km)) > FAR_DISTANCE_KM:
        fee *= FAR_SURCHARGE

    if express:
        fee *= EXPRESS_SURCHARGE

    return int(fee.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


if __name__ == "__main__":
    examples = [
        (500, 10, False),     # 4000
        (1000, 10, False),    # 4000
        (3000, 10, False),    # 8000
        (5000, 10, False),    # 8000
        (6000, 10, False),    # 8000 + 1500 = 9500
        (6000, 150, False),   # 9500 * 1.2 = 11400
        (6000, 150, True),    # 11400 * 1.5 = 17100
        (30000, 10, True),    # (8000 + 25*1500) * 1.5 = 68250
    ]
    for w, d, e in examples:
        print(f"weight={w:>6} g  distance={d:>4} km  express={e!s:<5}  ->  {shipping_fee(w, d, e)} satang")
