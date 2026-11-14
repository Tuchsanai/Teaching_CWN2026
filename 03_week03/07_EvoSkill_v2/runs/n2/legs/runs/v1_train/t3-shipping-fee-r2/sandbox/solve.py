"""BaanKafe: shipping_fee(weight_g, distance_km, express) -> จำนวนเต็มสตางค์"""
import json
import math
import sys
from fractions import Fraction


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def shipping_fee(weight_g, distance_km, express):
    need_int(weight_g, "weight_g", 1, 30000)
    # distance: จำนวนจริงไม่ติดลบ (int/float ที่จำกัด) ไม่รับ bool/str
    if type(distance_km) not in (int, float):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if type(distance_km) is float and not math.isfinite(distance_km):
        raise ValueError("distance_km ต้องเป็นค่าจำกัด")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")
    need_bool(express, "express")
    # สมมติฐาน (นโยบายร้าน): ส่งด่วนรับไม่เกิน 20,000 กรัม
    if express and weight_g > 20000:
        raise ValueError("ส่งด่วนรับน้ำหนักไม่เกิน 20,000 กรัม")
    # สมมติฐาน: ระยะ 0 = รับเองที่ร้าน ค่าส่ง 0
    if distance_km == 0:
        return 0

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction(weight_g - 5000, 1000) * 1500
    if Fraction(distance_km) > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return half_up(fee)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = shipping_fee(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
