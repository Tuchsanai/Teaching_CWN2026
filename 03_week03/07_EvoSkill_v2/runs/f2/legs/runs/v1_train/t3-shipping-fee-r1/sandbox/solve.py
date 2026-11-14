import json
import math
import sys
from fractions import Fraction


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    if type(weight_g) is not int or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม 1-30000")
    if type(distance_km) not in (int, float) or not math.isfinite(distance_km) or distance_km < 0:
        raise ValueError("distance_km ต้องเป็นตัวเลขตั้งแต่ 0")
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น True/False")

    # สมมติ: ระยะ 0 กม. = ลูกค้ามารับเองที่ร้าน ค่าส่ง 0
    if distance_km == 0:
        return 0

    if weight_g <= 1000:
        fee = Fraction(4000)  # สตางค์
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction(1500 * (weight_g - 5000), 1000)
    if Fraction(distance_km) > 100:
        fee *= Fraction(120, 100)
    if express:
        fee *= Fraction(150, 100)
    return half_up(fee)  # ปัดครั้งเดียวท้ายสุด half-up


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
