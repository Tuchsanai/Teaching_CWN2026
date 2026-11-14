"""BaanKafe: คิดค่าส่งเมล็ดกาแฟ (ผลลัพธ์เป็นสตางค์)"""
import json
import math
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ — เงินที่ลูกค้าจ่าย"""
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


def need_distance(value):
    # ระยะทางตั้งแต่ 0 รับ int หรือ float ที่จำกัด (ไม่รับ bool/nan/inf/str)
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("distance_km ไม่ถูกต้อง")
    elif type(value) is not int:
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if value < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")
    return Fraction(value)


def shipping_fee(weight_g, distance_km, express):
    need_int(weight_g, "weight_g", 1, 30000)
    distance = need_distance(distance_km)
    need_bool(express, "express")
    # สมมติฐาน (นโยบายร้าน): ส่งด่วนรับไม่เกิน 20,000 g; ระยะ 0 = รับเองที่ร้าน ค่าส่ง 0
    if express and weight_g > 20000:
        raise ValueError("ส่งด่วนรับน้ำหนักไม่เกิน 20,000 กรัม")
    if distance == 0:
        return 0

    if weight_g <= 1000:
        baht = Fraction(40)
    elif weight_g <= 5000:
        baht = Fraction(80)
    else:
        baht = 80 + Fraction(weight_g - 5000, 1000) * 15

    if distance > 100:
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
