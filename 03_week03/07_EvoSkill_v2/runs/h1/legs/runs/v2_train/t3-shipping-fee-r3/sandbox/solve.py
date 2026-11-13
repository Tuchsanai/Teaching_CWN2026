"""คิดค่าส่งเมล็ดกาแฟของ BaanKafe

shipping_fee(weight_g, distance_km, express) -> int (จำนวนเต็มสตางค์)

กติกา (ตามสเปก):
- น้ำหนัก 1..30,000 กรัม
  - ไม่เกิน 1,000 กรัม: 40 บาท
  - 1,001..5,000 กรัม: 80 บาท
  - เกิน 5,000 กรัม: 80 บาท + ส่วนที่เกิน 5,000 กรัม คิดตามสัดส่วน กิโลกรัมละ 15 บาท
- ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (คูณ 1.2)
- ส่งด่วน (express=True) คิดเพิ่ม 50% (คูณ 1.5) คูณต่อจากข้อก่อน
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ ปัดครึ่งขึ้นครั้งเดียวตอนท้าย

การคำนวณใช้ Fraction ทั้งหมด ไม่ใช้ float
"""

import json
import sys
from fractions import Fraction


def _require_int(value, label, lo=None, hi=None):
    if type(value) is not int:
        raise ValueError(f"{label} ต้องเป็นจำนวนเต็ม")
    if lo is not None and value < lo:
        raise ValueError(f"{label} ต้องไม่น้อยกว่า {lo}")
    if hi is not None and value > hi:
        raise ValueError(f"{label} ต้องไม่เกิน {hi}")
    return value


def _require_flag(value, label):
    if type(value) is not bool:
        raise ValueError(f"{label} ต้องเป็น True หรือ False")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม สำหรับค่าที่ไม่ติดลบ"""
    return int((Fraction(x) * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    weight_g = _require_int(weight_g, "weight_g", lo=1, hi=30000)
    distance_km = _require_int(distance_km, "distance_km", lo=0)
    express = _require_flag(express, "express")

    # ฐานค่าส่งเป็นสตางค์ (บาท × 100)
    if weight_g <= 1000:
        base = Fraction(40 * 100)
    elif weight_g <= 5000:
        base = Fraction(80 * 100)
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 กรัม = 3/2 สตางค์ต่อกรัม
        base = Fraction(80 * 100) + Fraction(weight_g - 5000) * Fraction(3, 2)

    fee = base
    if distance_km > 100:
        fee *= Fraction(6, 5)   # +20%
    if express:
        fee *= Fraction(3, 2)   # +50% คูณต่อจากข้อก่อน

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
