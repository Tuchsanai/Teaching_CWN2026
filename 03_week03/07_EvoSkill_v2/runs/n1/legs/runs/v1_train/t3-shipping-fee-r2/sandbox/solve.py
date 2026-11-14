"""BaanKafe shipping_fee — คืนค่าส่งเป็นจำนวนเต็มสตางค์

สมมติฐาน:
- weight_g ต้องเป็น int 1–30,000 (bool/float/str ถูกปฏิเสธ)
- distance_km เป็น int หรือ float ที่จำกัด >= 0 (bool/str/nan/inf ปฏิเสธ); 0 ใช้สูตรปกติ
- ระยะทาง "เกิน 100" ใช้ > 100 (พอดี 100 ไม่คิดเพิ่ม)
- ค่าส่งเป็นเงินที่ลูกค้าจ่าย -> คำนวณด้วย Fraction แล้วปัดครึ่งขึ้นครั้งเดียวตอนท้าย
- ส่งด่วนใช้ได้ทุกน้ำหนักภายในช่วง
"""
import json
import math
import sys
from fractions import Fraction


def half_up(x):
    return int((Fraction(x) * 2 + 1) // 2)


def shipping_fee(weight_g, distance_km, express):
    if type(weight_g) is not int or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม 1–30000")
    if type(distance_km) not in (int, float) or (
        type(distance_km) is float and not math.isfinite(distance_km)
    ) or distance_km < 0:
        raise ValueError("distance_km ต้องเป็นตัวเลข >= 0")
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น True หรือ False")

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        # ส่วนเกิน 5000 กรัม กก.ละ 15 บาท = 1500 สตางค์/กก.
        fee = Fraction(8000) + Fraction(weight_g - 5000, 1000) * 1500
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
