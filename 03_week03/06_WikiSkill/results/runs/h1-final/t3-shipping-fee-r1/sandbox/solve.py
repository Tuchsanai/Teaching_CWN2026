"""ค่าส่งเมล็ดกาแฟ BaanKafe.

shipping_fee(weight_g, distance_km, express) -> จำนวนเต็มสตางค์

กติกา:
- น้ำหนัก 1–30,000 กรัม
  - ไม่เกิน 1,000 กรัม: 40 บาท
  - ไม่เกิน 5,000 กรัม: 80 บาท
  - เกิน 5,000 กรัม: 80 บาท + (กรัมที่เกิน 5,000 / 1,000) * 15 บาท (ตามสัดส่วนกรัม)
- ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
- ส่งด่วน (express=True) คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
- ปัดเศษแบบ half up ครั้งเดียวตอนท้าย แล้วคืนเป็นสตางค์
"""

import json
import math
import sys
from fractions import Fraction

WEIGHT_MIN_G = 1
WEIGHT_MAX_G = 30000
TIER_1_MAX_G = 1000
TIER_2_MAX_G = 5000
TIER_1_FEE = Fraction(40)           # บาท
TIER_2_FEE = Fraction(80)           # บาท
HEAVY_FEE_PER_KG = Fraction(15)     # บาทต่อกิโลกรัมที่เกิน 5,000 กรัม
DISTANCE_THRESHOLD_KM = Fraction(100)
DISTANCE_MULTIPLIER = Fraction(120, 100)   # +20%
EXPRESS_MULTIPLIER = Fraction(150, 100)    # +50%


def _half_up(x: Fraction) -> int:
    """ปัดเศษ half up (ค่าไม่ติดลบ) ของเศษส่วน x เป็นจำนวนเต็ม."""
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


def _distance(v, name):
    """ระยะทางเป็นจำนวนไม่ติดลบ (int หรือ float จำกัด); float แปลงผ่าน repr เพื่อให้เป็นเศษส่วนทศนิยมที่แม่นยำ."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError(f"{name} must be a number")
    if isinstance(v, float) and not math.isfinite(v):
        raise ValueError(f"{name} must be finite")
    if v < 0:
        raise ValueError(f"{name} must be >= 0")
    return Fraction(repr(v)) if isinstance(v, float) else Fraction(v)


def shipping_fee(weight_g, distance_km, express):
    w = _int(weight_g, "weight_g", WEIGHT_MIN_G, WEIGHT_MAX_G)
    d = _distance(distance_km, "distance_km")
    e = _bool(express, "express")

    # ขั้นค่าส่งตามน้ำหนัก (เก็บเป็นเศษส่วน ยังไม่ปัด)
    if w <= TIER_1_MAX_G:
        fee = TIER_1_FEE
    elif w <= TIER_2_MAX_G:
        fee = TIER_2_FEE
    else:
        fee = TIER_2_FEE + Fraction(w - TIER_2_MAX_G, 1000) * HEAVY_FEE_PER_KG

    # ระยะทางเกิน 100 กม. (ที่ 100 พอดีไม่คิดเพิ่ม)
    if d > DISTANCE_THRESHOLD_KM:
        fee *= DISTANCE_MULTIPLIER

    # ส่งด่วน
    if e:
        fee *= EXPRESS_MULTIPLIER

    # ปัดครั้งเดียวตอนท้าย: บาท -> สตางค์
    return _half_up(fee * 100)


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
