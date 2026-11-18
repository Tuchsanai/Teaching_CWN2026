"""shipping_fee · BaanKafe"""
import json
import sys
from fractions import Fraction


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็มสตางค์ (x ไม่ติดลบ)"""
    return int((Fraction(x) * 2 + 1) // 2)


def round_down(x):
    """ปัดลง (ใช้กับเงินที่ร้านจ่ายออก เช่นเงินคืน) x ไม่ติดลบ"""
    return int(Fraction(x) // 1)


def need_int(value, name, low=None, high=None):
    if type(value) is not int:  # bool และ float ไม่ใช่ int
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def shipping_fee(weight_g, distance_km, express):
    """ค่าส่งเป็นสตางค์ (int)
    นโยบาย: ตรวจ input ทุกตัวก่อน; S1 distance==0 = รับเองที่ร้าน -> 0;
    S2 express รับน้ำหนักไม่เกิน 20,000 g เกินนั้น ValueError;
    ส่วนเกิน 5,000 g คิดตามสัดส่วนกรัม (Fraction) คูณ 20%/50% ต่อเนื่อง แล้วปัด half-up ครั้งเดียว"""
    need_int(weight_g, "weight_g", 1, 30000)
    need_int(distance_km, "distance_km", 0)
    need_bool(express, "express")
    if express and weight_g > 20000:
        raise ValueError("ส่งด่วนรับน้ำหนักไม่เกิน 20,000 กรัม")
    if distance_km == 0:
        return 0
    if weight_g <= 1000:
        fee = Fraction(4000)
    elif weight_g <= 5000:
        fee = Fraction(8000)
    else:
        fee = Fraction(8000) + Fraction(1500 * (weight_g - 5000), 1000)
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
