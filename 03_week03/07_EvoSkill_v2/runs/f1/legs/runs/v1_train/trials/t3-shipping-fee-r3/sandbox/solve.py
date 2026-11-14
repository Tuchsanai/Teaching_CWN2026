"""BaanKafe shipping_fee — คืนค่าส่งเป็นสตางค์ (จำนวนเต็ม)"""
import json
import math
import sys
from fractions import Fraction


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    # ตรวจ input ก่อนเสมอ
    if type(weight_g) is not int or not (1 <= weight_g <= 30000):
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม 1-30000")
    if type(distance_km) not in (int, float) or (
        type(distance_km) is float and not math.isfinite(distance_km)
    ) or distance_km < 0:
        raise ValueError("distance_km ต้องเป็นตัวเลข >= 0")
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น True หรือ False")
    # กฎร้าน S2: ส่งด่วนรับไม่เกิน 20000 กรัม
    if express and weight_g > 20000:
        raise ValueError("ส่งด่วนรับน้ำหนักไม่เกิน 20000 กรัม")
    # กฎร้าน S1: ระยะ 0 = ลูกค้ารับเองที่ร้าน ค่าส่ง 0
    if distance_km == 0:
        return 0

    if weight_g <= 1000:
        baht = Fraction(40)
    elif weight_g <= 5000:
        baht = Fraction(80)
    else:
        baht = 80 + Fraction(weight_g - 5000, 1000) * 15
    if Fraction(distance_km) > 100:
        baht *= Fraction(120, 100)
    if express:
        baht *= Fraction(150, 100)
    return half_up(baht * 100)


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
