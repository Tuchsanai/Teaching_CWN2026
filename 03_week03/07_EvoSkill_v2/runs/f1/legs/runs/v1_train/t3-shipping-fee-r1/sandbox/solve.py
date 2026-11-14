import json
import math
import sys
from fractions import Fraction


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้นครั้งเดียวตอนท้าย)

    ข้อสันนิษฐาน: distance_km รับ int หรือ float ที่จำกัดค่า (ไม่ใช่ bool/NaN/inf);
    distance_km == 0 (รับเองที่ร้าน) -> ไม่คิดค่าส่ง คืน 0
    """
    if type(weight_g) is not int or not (1 <= weight_g <= 30000):
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม 1-30000")
    if type(distance_km) not in (int, float):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if type(distance_km) is float and not math.isfinite(distance_km):
        raise ValueError("distance_km ไม่ถูกต้อง")
    if distance_km < 0:
        raise ValueError("distance_km ต้อง >= 0")
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น True หรือ False")

    if distance_km == 0:
        return 0
    if weight_g <= 1000:
        fee = Fraction(40)
    elif weight_g <= 5000:
        fee = Fraction(80)
    else:
        fee = 80 + Fraction(weight_g - 5000, 1000) * 15
    if distance_km > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
    return half_up(fee * 100)


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
