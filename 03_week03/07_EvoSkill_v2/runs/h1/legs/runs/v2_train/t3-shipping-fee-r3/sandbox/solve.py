"""BaanKafe shipping fee calculator (ค่าส่งเมล็ดกาแฟ).

กติกา
- น้ำหนัก weight_g: จำนวนเต็ม 1..30000 กรัม
- ระยะทาง distance_km: จำนวนเต็ม >= 0 (กิโลเมตร)
- express: bool, True = ส่งด่วน
1. น้ำหนักไม่เกิน 1000 g            -> 40 บาท
2. น้ำหนักไม่เกิน 5000 g (และ > 1000 g) -> 80 บาท
3. น้ำหนักเกิน 5000 g               -> 80 บาท + (น้ำหนักเกิน 5000 g) * 15 บาท/กก. (คิดตามสัดส่วนกรัม)
4. ระยะทางเกิน 100 กม.              -> คิดเพิ่ม 20% ( คูณ 1.2)
5. ส่งด่วน                          -> คิดเพิ่ม 50% (คูณ 1.5 ต่อจากข้อ 4)
6. คืนค่าส่งเป็นจำนวนเต็มสตางค์ ปัดครึ่งขึ้นครั้งเดียวตอนท้ายสุด

การคำนวณ: ใช้ Fraction ทั้งหมด (ไม่ใช้ float) หน่วยคำนวณเป็นสตางค์
- 15 บาท/กก. = 1500 สตางค์/กก. = 1.5 สตางค์/กรัม
"""

import json
import sys
from fractions import Fraction
from math import floor

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30000
LONG_DISTANCE_KM = 100

FEE_UNDER_1KG_SATANG = 4000   # 40 บาท
FEE_UNDER_5KG_SATANG = 8000   # 80 บาท
HEAVY_RATE_SATANG_PER_G = Fraction(3, 2)  # 1.5 สตางค์/กรัม = 15 บาท/กก.

LONG_DISTANCE_MULTIPLIER = Fraction(120, 100)  # +20%
EXPRESS_MULTIPLIER = Fraction(150, 100)        # +50%


def _half_up(x):
    # ปัดครึ่งขึ้น สำหรับ x >= 0: 2.4 -> 2, 2.5 -> 3
    return floor(Fraction(x) + Fraction(1, 2))


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ ไม่ถูกต้องจะ raise ValueError"""
    if type(weight_g) is not int:
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม (int)")
    if type(distance_km) is not int:
        raise ValueError("distance_km ต้องเป็นจำนวนเต็ม (int)")
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น bool")
    if not (MIN_WEIGHT_G <= weight_g <= MAX_WEIGHT_G):
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1 ถึง 30000 กรัม")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    # ค่าส่งตามน้ำหนัก (สตางค์)
    if weight_g <= 1000:
        fee = Fraction(FEE_UNDER_1KG_SATANG)
    elif weight_g <= 5000:
        fee = Fraction(FEE_UNDER_5KG_SATANG)
    else:
        fee = FEE_UNDER_5KG_SATANG + (weight_g - 5000) * HEAVY_RATE_SATANG_PER_G

    # ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if distance_km > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_MULTIPLIER

    # ส่งด่วน คิดเพิ่ม 50% (ทบต้นจากข้อก่อน)
    if express:
        fee *= EXPRESS_MULTIPLIER

    # ปัดครั้งเดียวตอนท้ายสุด
    return _half_up(fee)


def main():
    try:
        args = json.loads(sys.stdin.read())
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = shipping_fee(**args)
    except (ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
