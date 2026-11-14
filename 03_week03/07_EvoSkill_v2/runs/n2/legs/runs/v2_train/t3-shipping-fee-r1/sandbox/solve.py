"""BaanKafe: ค่าส่งเมล็ดกาแฟ (หน่วยเงินที่คืน = สตางค์)

สมมติฐานตอนโจทย์เงียบ (ตามนโยบายร้าน):
- distance_km == 0 = รับเองที่ร้าน -> 0 (หลังตรวจ input)
- ส่งด่วนรับน้ำหนักไม่เกิน 20,000 กรัม เกินแล้ว ValueError
- ค่าส่งเป็นเงินที่ลูกค้าจ่าย -> ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
- distance_km ต้องเป็น int (ไม่รับ float/bool/str)
"""
import json
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
    need_int(distance_km, "distance_km", 0)
    need_bool(express, "express")
    if express and weight_g > 20000:
        raise ValueError("ส่งด่วนรับน้ำหนักไม่เกิน 20,000 กรัม")
    if distance_km == 0:
        return 0
    if weight_g <= 1000:
        baht = Fraction(40)
    elif weight_g <= 5000:
        baht = Fraction(80)
    else:
        baht = 80 + Fraction(weight_g - 5000, 1000) * 15
    amount = baht * 100  # สตางค์
    if distance_km > 100:
        amount *= Fraction(120, 100)
    if express:
        amount *= Fraction(150, 100)
    return half_up(amount)


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
