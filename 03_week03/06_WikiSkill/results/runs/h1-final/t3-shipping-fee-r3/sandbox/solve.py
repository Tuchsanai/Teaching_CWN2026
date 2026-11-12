"""คิดค่าส่งเมล็ดกาแฟของ BaanKafe

หน่วยที่ใช้ภายใน: สตางค์ (1 บาท = 100 สตางค์)
ผลลัพธ์: จำนวนเต็มสตางค์ ปัดแบบ half up ครั้งเดียวตอนท้าย
"""

import json
import sys
from fractions import Fraction


# ค่าส่งฐาน (สตางค์)
FEE_UP_TO_1000_G = 4000   # ไม่เกิน 1,000 กรัม = 40 บาท
FEE_UP_TO_5000_G = 8000   # ไม่เกิน 5,000 กรัม = 80 บาท
EXCESS_PER_G = Fraction(1500, 1000)  # 15 บาท/กก. = 1.5 สตางค์/กรัม ของส่วนที่เกิน 5,000 กรัม

LONG_DISTANCE_KM = 100
LONG_DISTANCE_MULTIPLIER = Fraction(120, 100)  # เพิ่ม 20%
EXPRESS_MULTIPLIER = Fraction(150, 100)        # เพิ่ม 50%


def _half_up(x: Fraction) -> int:
    """ปัดเศษ half up (x >= 0) เป็นจำนวนเต็ม"""
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def _int(v, name, lo=None, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be an integer")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def _bool(v, name):
    if not isinstance(v, bool):
        raise ValueError(f"{name} must be a bool")
    return v


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์

    weight_g    : น้ำหนักเป็นกรัม (int, 1–30000)
    distance_km : ระยะทางเป็นกิโลเมตร (int, ตั้งแต่ 0)
    express     : True = ส่งด่วน
    """
    weight_g = _int(weight_g, "weight_g", lo=1, hi=30000)
    distance_km = _int(distance_km, "distance_km", lo=0)
    express = _bool(express, "express")

    # ค่าส่งตามน้ำหนัก (ยังไม่ปัด)
    if weight_g <= 1000:
        fee = Fraction(FEE_UP_TO_1000_G)
    elif weight_g <= 5000:
        fee = Fraction(FEE_UP_TO_5000_G)
    else:
        fee = FEE_UP_TO_5000_G + EXCESS_PER_G * (weight_g - 5000)

    # ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if distance_km > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_MULTIPLIER

    # ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
    if express:
        fee *= EXPRESS_MULTIPLIER

    # ปัดครั้งเดียวตอนท้าย
    return _half_up(fee)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = shipping_fee(**data)
        out = json.dumps({"ok": True, "result": result})
    except Exception as e:  # รวม JSON เสีย, key เกิน/ขาด, ValueError
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
