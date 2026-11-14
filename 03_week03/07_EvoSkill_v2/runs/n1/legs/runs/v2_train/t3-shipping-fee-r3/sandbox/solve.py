"""BaanKafe shipping_fee (หน่วยสตางค์)

สมมติฐาน (brief เงียบ ใช้มาตรฐานร้าน):
1. distance_km == 0 → ลูกค้ารับเองที่ร้าน ค่าส่ง 0 (ตรวจ input ก่อนเสมอ)
2. ส่งด่วนได้ไม่เกิน 20,000 กรัม (2/3 ของน้ำหนักสูงสุด) เกินนี้ ValueError
3. ค่าส่งเป็นเงินที่ลูกค้าจ่าย → ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
4. ทุกตัวเลขต้องเป็น int (ปฏิเสธ float/str/bool/None)
"""
import json
import sys
from fractions import Fraction

MAX_EXPRESS_WEIGHT_G = 20000


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
    if express and weight_g > MAX_EXPRESS_WEIGHT_G:
        raise ValueError("พัสดุหนักเกินกว่าจะส่งด่วนได้")
    if distance_km == 0:
        return 0

    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction(weight_g - 5000, 1000) * 1500
    if distance_km > 100:
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
