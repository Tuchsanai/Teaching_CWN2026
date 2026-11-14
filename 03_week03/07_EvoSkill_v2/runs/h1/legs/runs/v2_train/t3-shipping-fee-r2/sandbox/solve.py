"""ค่าส่งเมล็ดกาแฟ BaanKafe

กติกา:
- น้ำหนัก weight_g: จำนวนเต็ม 1–30,000 กรัม
- ระยะทาง distance_km: จำนวนเต็มตั้งแต่ 0 กิโลเมตร
- express: True = ส่งด่วน, False = ส่งธรรมดา
- ไม่เกิน 1,000 กรัม  -> 40 บาท
- ไม่เกิน 5,000 กรัม  -> 80 บาท
- เกิน 5,000 กรัม     -> 80 บาท + (น้ำหนักที่เกิน 5,000 กรัม) * 15 บาท/กก. (คิดตามสัดส่วนของกรัม)
- ระยะทาง "เกิน 100 กม." (> 100) -> คิดเพิ่ม 20% (คูณ 1.2)
- ส่งด่วน -> คิดเพิ่ม 50% (คูณ 1.5) คูณต่อจากข้อก่อนหน้า
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ ปัดครั้งเดียวตอนท้ายแบบครึ่งขึ้น (half up)

การคำนวณใช้ Fraction ทั้งหมด ไม่ใช้ float
"""

import json
import sys
from fractions import Fraction
from math import floor

SATANG_PER_BAHT = 100

BASE_LIGHT_SATANG = 40 * SATANG_PER_BAHT   # ไม่เกิน 1,000 กรัม
BASE_MEDIUM_SATANG = 80 * SATANG_PER_BAHT  # ไม่เกิน 5,000 กรัม
EXCESS_PER_KG_SATANG = 15 * SATANG_PER_BAHT  # 15 บาท/กก. = 1500 สตางค์/1000 กรัม

MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000


def _half_up(x):
    """ปัดครึ่งขึ้น สำหรับ x >= 0: 2.4 -> 2, 2.5 -> 3"""
    return floor(Fraction(x) + Fraction(1, 2))


def shipping_fee(weight_g, distance_km, express):
    # ---- ตรวจ input แบบเข้มงวด ----
    if type(weight_g) is not int:
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม (int)")
    if type(distance_km) is not int:
        raise ValueError("distance_km ต้องเป็นจำนวนเต็ม (int)")
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น True หรือ False")
    if not (MIN_WEIGHT_G <= weight_g <= MAX_WEIGHT_G):
        raise ValueError("weight_g ต้องอยู่ในช่วง 1–30000 กรัม")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    # ---- คิดค่าส่งตามน้ำหนัก (สตางค์) ----
    w = Fraction(weight_g)
    if w <= 1000:
        fee = Fraction(BASE_LIGHT_SATANG)
    elif w <= 5000:
        fee = Fraction(BASE_MEDIUM_SATANG)
    else:
        excess_g = w - 5000
        fee = BASE_MEDIUM_SATANG + excess_g * EXCESS_PER_KG_SATANG / 1000

    # ---- ระยะทางเกิน 100 กม. คิดเพิ่ม 20% ----
    if distance_km > 100:
        fee *= Fraction(120, 100)

    # ---- ส่งด่วนคิดเพิ่ม 50% (คูณต่อจากข้อก่อน) ----
    if express:
        fee *= Fraction(150, 100)

    # ---- ปัดครั้งเดียวตอนท้าย ----
    return _half_up(fee)


def main():
    try:
        raw = sys.stdin.read()
        args = json.loads(raw)
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
