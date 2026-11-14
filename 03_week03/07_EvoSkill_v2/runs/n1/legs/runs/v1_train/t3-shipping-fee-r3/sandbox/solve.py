"""BaanKafe shipping_fee -> จำนวนเต็มสตางค์

สมมติฐาน:
- distance_km รับ int หรือ float (ไม่รวม bool) ที่ไม่ติดลบและจำกัดค่า (ไม่ NaN/inf); 0 ใช้สูตรปกติ
- weight_g ต้องเป็น int 1-30000; express ต้องเป็น bool
- ค่าส่งคือเงินที่ลูกค้าจ่าย -> ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
- ตัวคูณ (ไกล 1.2, ด่วน 1.5) คูณสะสม; "เกิน 100 กม." ใช้ >
"""
import json
import math
import sys
from fractions import Fraction


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    if type(weight_g) is not int or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม 1-30000")
    if type(distance_km) not in (int, float):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if type(distance_km) is float and not math.isfinite(distance_km):
        raise ValueError("distance_km ต้องเป็นจำนวนจำกัด")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น True หรือ False")

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์/กก. ตามสัดส่วนกรัม
        fee = 8000 + Fraction((weight_g - 5000) * 1500, 1000)
    if Fraction(distance_km) > 100:
        fee *= Fraction(6, 5)
    if express:
        fee *= Fraction(3, 2)
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
