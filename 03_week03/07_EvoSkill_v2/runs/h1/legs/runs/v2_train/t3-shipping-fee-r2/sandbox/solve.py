"""ค่าส่งเมล็ดกาแฟ BaanKafe

shipping_fee(weight_g, distance_km, express) -> int (หน่วยเป็นสตางค์)

กติกา (ตามลำดับ):
1. ฐานตามน้ำหนัก
   - ไม่เกิน 1,000 กรัม          -> 40 บาท
   - 1,001 ถึง 5,000 กรัม        -> 80 บาท
   - เกิน 5,000 กรัม             -> 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน 5,000 (คิดตามสัดส่วนของกรัม)
2. ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (ที่ 100 กม. พอดีไม่เพิ่ม)
3. ส่งด่วน (express=True) คิดเพิ่ม 50% คูณต่อจากข้อ 2
4. ปัดครึ่งขึ้นเป็นสตางค์ครั้งเดียวตอนท้าย

การคำนวณใช้ Fraction ทั้งหมด ไม่ใช้ float
"""

import json
import sys
from fractions import Fraction

MAX_WEIGHT_G = 30000
LONG_DISTANCE_KM = 100
LIGHT_LIMIT_G = 1000
MEDIUM_LIMIT_G = 5000
BASE_LIGHT_SATANG = 4000          # 40 บาท
BASE_MEDIUM_SATANG = 8000         # 80 บาท
EXTRA_PER_KG_SATANG = 1500        # 15 บาทต่อกิโลกรัม
LONG_DISTANCE_MULT = Fraction(6, 5)   # +20%
EXPRESS_MULT = Fraction(3, 2)         # +50%


def _require_int(value, label, lo=None, hi=None):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and value > hi:
        raise ValueError(f"{label} ต้องไม่เกิน {hi}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม สำหรับค่าที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    weight_g = _require_int(weight_g, "weight_g", 1, MAX_WEIGHT_G)
    distance_km = _require_int(distance_km, "distance_km", 0)
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น True หรือ False")

    if weight_g <= LIGHT_LIMIT_G:
        fee = Fraction(BASE_LIGHT_SATANG)
    elif weight_g <= MEDIUM_LIMIT_G:
        fee = Fraction(BASE_MEDIUM_SATANG)
    else:
        extra_g = weight_g - MEDIUM_LIMIT_G
        fee = BASE_MEDIUM_SATANG + Fraction(extra_g * EXTRA_PER_KG_SATANG, 1000)

    if distance_km > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_MULT

    if express:
        fee *= EXPRESS_MULT

    return _half_up(fee)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = shipping_fee(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
